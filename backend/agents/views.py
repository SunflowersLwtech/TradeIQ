"""
Agent Query REST API Endpoint
Exposes the DeepSeek function-calling router via HTTP
+ Agent Team pipeline endpoints
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .router import route_query
from .agent_team import (
    run_pipeline,
    market_monitor_detect,
    analyst_analyze,
    portfolio_advisor_interpret,
    content_creator_generate,
    VolatilityEvent,
    AnalysisReport,
)
from dataclasses import asdict
import json


class AgentQueryView(APIView):
    """
    POST /api/agents/query/
    {
        "query": "Why did EUR/USD spike today?",
        "agent_type": "market",  // "market", "behavior", "content"
        "user_id": "optional-uuid",
        "context": {}  // optional additional context
    }
    """
    permission_classes = [AllowAny]  # Demo mode - no auth required

    def post(self, request):
        query = request.data.get("query", "")
        agent_type = request.data.get("agent_type", "market")
        user_id = request.data.get("user_id")
        context = request.data.get("context", {})

        if not query:
            return Response(
                {"error": "query is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = route_query(
            query=query,
            agent_type=agent_type,
            user_id=user_id,
            context=context,
        )

        return Response(result)


class AgentChatView(APIView):
    """
    POST /api/agents/chat/
    Stateless chat - each request is independent.
    {
        "message": "Why did EUR/USD move?",
        "agent_type": "market",
        "user_id": "optional-uuid"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        message = request.data.get("message", "")
        agent_type = request.data.get("agent_type", "auto")
        user_id = request.data.get("user_id")

        if not message:
            return Response(
                {"error": "message is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Auto-detect agent type based on message content
        if agent_type == "auto":
            msg_lower = message.lower()
            if any(w in msg_lower for w in ["pattern", "behavior", "nudge", "revenge", "overtrad", "habit", "streak", "discipline"]):
                agent_type = "behavior"
            elif any(w in msg_lower for w in ["post", "bluesky", "content", "thread", "persona", "publish", "social"]):
                agent_type = "content"
            else:
                agent_type = "market"

        result = route_query(
            query=message,
            agent_type=agent_type,
            user_id=user_id,
        )

        return Response({
            "message": result.get("response", ""),
            "agent_type": agent_type,
            "tools_used": result.get("tools_used", []),
            "source": result.get("source", ""),
        })


# ─── Agent Team Pipeline Endpoints ────────────────────────────────────

class AgentTeamPipelineView(APIView):
    """
    POST /api/agents/pipeline/
    Run the full 4-agent pipeline:
      Monitor → Analyst → Advisor → Content Creator

    Body:
    {
        "instruments": ["BTC/USD"],        // optional – defaults to major pairs
        "custom_event": {                  // optional – manual trigger
            "instrument": "BTC/USD",
            "price": 97500,
            "change_pct": 5.2
        },
        "user_portfolio": [...],           // optional – user positions
        "skip_content": false              // optional – skip tweet generation
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        instruments = request.data.get("instruments")
        custom_event = request.data.get("custom_event")
        user_portfolio = request.data.get("user_portfolio")
        skip_content = request.data.get("skip_content", False)

        result = run_pipeline(
            instruments=instruments,
            custom_event=custom_event,
            user_portfolio=user_portfolio,
            skip_content=skip_content,
        )
        return Response(asdict(result))


class AgentMonitorView(APIView):
    """
    POST /api/agents/monitor/
    Run only the Market Monitor agent.

    Body:
    {
        "instruments": ["EUR/USD", "BTC/USD"],
        "custom_event": null
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        instruments = request.data.get("instruments")
        custom_event = request.data.get("custom_event")

        event = market_monitor_detect(
            instruments=instruments,
            custom_event=custom_event,
        )
        if event is None:
            return Response({"status": "no_event", "message": "No significant volatility detected."})

        return Response({"status": "detected", "event": asdict(event)})


class AgentAnalystView(APIView):
    """
    POST /api/agents/analyst/
    Run only the Analyst agent on a given event.

    Body:
    {
        "instrument": "BTC/USD",
        "current_price": 97500,
        "price_change_pct": 5.2,
        "direction": "spike",
        "magnitude": "high"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            event = VolatilityEvent(
                instrument=request.data.get("instrument", "BTC/USD"),
                current_price=request.data.get("current_price"),
                price_change_pct=request.data.get("price_change_pct", 0.0),
                direction=request.data.get("direction", "spike"),
                magnitude=request.data.get("magnitude", "medium"),
            )
            report = analyst_analyze(event)
            return Response(asdict(report))
        except Exception as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AgentAdvisorView(APIView):
    """
    POST /api/agents/advisor/
    Run only the Portfolio Advisor agent.

    Body:
    {
        "analysis_report": { ... },   // AnalysisReport fields
        "user_portfolio": [ ... ]     // optional
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        report_data = request.data.get("analysis_report", {})
        user_portfolio = request.data.get("user_portfolio")

        try:
            report = AnalysisReport(
                instrument=report_data.get("instrument", ""),
                event_summary=report_data.get("event_summary", ""),
                root_causes=report_data.get("root_causes", []),
                news_sources=report_data.get("news_sources", []),
                sentiment=report_data.get("sentiment", "neutral"),
                sentiment_score=report_data.get("sentiment_score", 0.0),
                key_data_points=report_data.get("key_data_points", []),
            )
            insight = portfolio_advisor_interpret(report, user_portfolio)
            return Response(asdict(insight))
        except Exception as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AgentContentView(APIView):
    """
    POST /api/agents/content-gen/
    Run only the Content Creator agent.

    Body:
    {
        "analysis_report": { ... },
        "personalized_insight": { ... }  // optional
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        report_data = request.data.get("analysis_report", {})
        insight_data = request.data.get("personalized_insight")

        try:
            report = AnalysisReport(
                instrument=report_data.get("instrument", ""),
                event_summary=report_data.get("event_summary", ""),
                root_causes=report_data.get("root_causes", []),
                news_sources=report_data.get("news_sources", []),
                sentiment=report_data.get("sentiment", "neutral"),
                sentiment_score=report_data.get("sentiment_score", 0.0),
                key_data_points=report_data.get("key_data_points", []),
            )

            from .agent_team import PersonalizedInsight
            insight = None
            if insight_data:
                insight = PersonalizedInsight(
                    instrument=insight_data.get("instrument", ""),
                    impact_summary=insight_data.get("impact_summary", ""),
                    affected_positions=insight_data.get("affected_positions", []),
                    risk_assessment=insight_data.get("risk_assessment", "medium"),
                    suggestions=insight_data.get("suggestions", []),
                )

            commentary = content_creator_generate(report, insight)
            return Response(asdict(commentary))
        except Exception as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
