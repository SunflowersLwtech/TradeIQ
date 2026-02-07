"""
Agent Team Pipeline for TradeIQ
4 Agents working in sequence:
  1. Market Monitor  → detects volatility events
  2. Analyst         → root-cause analysis of the event
  3. Portfolio Advisor → personalised interpretation for user holdings
  4. Content Creator  → generates English market commentary for Bluesky

Each agent has a clear input/output contract so they can be tested
independently or chained via `run_pipeline()`.
"""

from __future__ import annotations

import json
import traceback
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.llm_client import get_llm_client
from agents.prompts import MASTER_COMPLIANCE_RULES
from market.tools import (
    fetch_price_data,
    search_news,
    get_sentiment,
)


# ─── Data contracts between agents ───────────────────────────────────

@dataclass
class VolatilityEvent:
    """Output of Market Monitor Agent."""
    instrument: str
    current_price: Optional[float]
    price_change_pct: float
    direction: str  # "spike" | "drop"
    magnitude: str  # "high" | "medium"
    detected_at: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.detected_at:
            self.detected_at = datetime.now().isoformat()


@dataclass
class AnalysisReport:
    """Output of Analyst Agent."""
    instrument: str
    event_summary: str
    root_causes: List[str]
    news_sources: List[Dict[str, str]]
    sentiment: str          # "bullish" | "bearish" | "neutral"
    sentiment_score: float  # -1.0 to 1.0
    key_data_points: List[str]
    generated_at: str = ""

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()


@dataclass
class PersonalizedInsight:
    """Output of Portfolio Advisor Agent."""
    instrument: str
    impact_summary: str
    affected_positions: List[Dict[str, Any]]
    risk_assessment: str    # "high" | "medium" | "low"
    suggestions: List[str]  # educational, never predictive
    generated_at: str = ""

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()


@dataclass
class MarketCommentary:
    """Output of Content Creator Agent."""
    post: str
    hashtags: List[str]
    data_points: List[str]
    platform: str = "bluesky"
    published: bool = False
    bluesky_uri: str = ""
    bluesky_url: str = ""
    generated_at: str = ""

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()


@dataclass
class PipelineResult:
    """Full pipeline output – every stage's result bundled together."""
    status: str  # "success" | "partial" | "error"
    volatility_event: Optional[Dict[str, Any]] = None
    analysis_report: Optional[Dict[str, Any]] = None
    personalized_insight: Optional[Dict[str, Any]] = None
    market_commentary: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    pipeline_started_at: str = ""
    pipeline_finished_at: str = ""

    def __post_init__(self):
        if not self.pipeline_started_at:
            self.pipeline_started_at = datetime.now().isoformat()


# ─── Agent 1: Market Monitor ─────────────────────────────────────────

MONITOR_INSTRUMENTS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "BTC/USD",
    "ETH/USD", "GOLD", "Volatility 75",
]

# Threshold (%) for volatility detection per asset class
_THRESHOLDS = {
    "BTC/USD": 3.0,
    "ETH/USD": 4.0,
    "Volatility 75": 2.0,
    "Volatility 100": 2.0,
    "default": 0.5,
}


def _threshold(instrument: str) -> float:
    return _THRESHOLDS.get(instrument, _THRESHOLDS["default"])


def market_monitor_detect(
    instruments: Optional[List[str]] = None,
    custom_event: Optional[Dict[str, Any]] = None,
) -> Optional[VolatilityEvent]:
    """
    Agent 1 – Market Monitor.

    Scans instruments for significant price movements.
    Can also accept a *custom_event* dict for manual/demo triggers.

    Returns the most significant VolatilityEvent found, or None.
    """
    # ── Manual / demo trigger ──
    if custom_event:
        return VolatilityEvent(
            instrument=custom_event.get("instrument", "BTC/USD"),
            current_price=custom_event.get("price"),
            price_change_pct=custom_event.get("change_pct", 5.0),
            direction="spike" if custom_event.get("change_pct", 5.0) > 0 else "drop",
            magnitude="high" if abs(custom_event.get("change_pct", 5.0)) >= 3.0 else "medium",
            raw_data=custom_event,
        )

    # ── Automatic scan ──
    instruments = instruments or MONITOR_INSTRUMENTS
    events: List[VolatilityEvent] = []

    for inst in instruments:
        try:
            price_data = fetch_price_data(inst)
            price = price_data.get("price")
            if price is None:
                continue

            # Compare to a reference price embedded in mock data or use a
            # simple heuristic: since we have single tick data, we simulate
            # change detection via a small random variance check.  In
            # production this would compare against a rolling window stored
            # in Redis / DB.
            # For demo, generate a simulated change based on sentiment.
            sentiment_data = get_sentiment(inst)
            score = sentiment_data.get("score", 0.0)
            simulated_change = score * 2.5  # rough mapping

            threshold = _threshold(inst)
            if abs(simulated_change) >= threshold:
                events.append(
                    VolatilityEvent(
                        instrument=inst,
                        current_price=price,
                        price_change_pct=round(simulated_change, 2),
                        direction="spike" if simulated_change > 0 else "drop",
                        magnitude="high" if abs(simulated_change) >= threshold * 2 else "medium",
                        raw_data=price_data,
                    )
                )
        except Exception as exc:
            print(f"[MarketMonitor] Error scanning {inst}: {exc}")

    if not events:
        return None

    # Return the most significant event
    events.sort(key=lambda e: abs(e.price_change_pct), reverse=True)
    return events[0]


# ─── Agent 2: Analyst ─────────────────────────────────────────────────

_ANALYST_SYSTEM = f"""You are TradeIQ's Senior Market Analyst.
Given a volatility event, determine the ROOT CAUSES using news, sentiment,
and market context. Be specific and cite sources.

{MASTER_COMPLIANCE_RULES}

Output a JSON object:
{{
  "event_summary": "<1 sentence describing what happened>",
  "root_causes": ["cause 1", "cause 2", ...],
  "key_data_points": ["data point 1", "data point 2", ...],
  "sentiment": "bullish" | "bearish" | "neutral",
  "sentiment_score": <float -1.0 to 1.0>
}}
"""


def analyst_analyze(event: VolatilityEvent) -> AnalysisReport:
    """
    Agent 2 – Analyst.

    Takes a VolatilityEvent and produces a structured AnalysisReport
    by combining news search, sentiment analysis, and LLM reasoning.
    """
    llm = get_llm_client()

    # Gather context data
    news = search_news(event.instrument, limit=5)
    sentiment = get_sentiment(event.instrument)

    news_context = "\n".join(
        f"- [{a.get('source', '?')}] {a.get('title', 'N/A')}: {(a.get('description') or '')[:120]}"
        for a in news[:5]
    ) or "No recent news found."

    prompt = f"""Volatility Event detected:
- Instrument: {event.instrument}
- Current Price: {event.current_price}
- Change: {event.price_change_pct:+.2f}%
- Direction: {event.direction}
- Magnitude: {event.magnitude}

Sentiment Data: {json.dumps(sentiment, default=str)}

Recent News:
{news_context}

Analyze the root causes of this volatility event. Return JSON only."""

    try:
        response = llm.simple_chat(
            system_prompt=_ANALYST_SYSTEM,
            user_message=prompt,
            temperature=0.4,
            max_tokens=600,
        )
        parsed = _parse_json(response)

        return AnalysisReport(
            instrument=event.instrument,
            event_summary=parsed.get("event_summary", f"{event.instrument} moved {event.price_change_pct:+.2f}%"),
            root_causes=parsed.get("root_causes", ["Unable to determine specific causes"]),
            news_sources=[{"title": a.get("title", ""), "url": a.get("url", ""), "source": a.get("source", "")} for a in news[:5]],
            sentiment=parsed.get("sentiment", sentiment.get("sentiment", "neutral")),
            sentiment_score=float(parsed.get("sentiment_score", sentiment.get("score", 0.0))),
            key_data_points=parsed.get("key_data_points", []),
        )
    except Exception as exc:
        print(f"[Analyst] Error: {exc}")
        return AnalysisReport(
            instrument=event.instrument,
            event_summary=f"{event.instrument} experienced a {event.magnitude} {event.direction} of {event.price_change_pct:+.2f}%",
            root_causes=["Analysis unavailable – LLM error"],
            news_sources=[{"title": a.get("title", ""), "url": a.get("url", "")} for a in news[:3]],
            sentiment=sentiment.get("sentiment", "neutral"),
            sentiment_score=float(sentiment.get("score", 0.0)),
            key_data_points=[f"Price: {event.current_price}"],
        )


# ─── Agent 3: Portfolio Advisor ────────────────────────────────────────

_ADVISOR_SYSTEM = f"""You are TradeIQ's Portfolio Advisor.
Given a market analysis report AND a user's portfolio, provide a
personalised impact assessment. Be educational, not predictive.

{MASTER_COMPLIANCE_RULES}

Output a JSON object:
{{
  "impact_summary": "<1-2 sentences on how this event relates to the user's positions>",
  "risk_assessment": "high" | "medium" | "low",
  "suggestions": ["educational suggestion 1", "suggestion 2", ...]
}}
"""


def portfolio_advisor_interpret(
    report: AnalysisReport,
    user_portfolio: Optional[List[Dict[str, Any]]] = None,
) -> PersonalizedInsight:
    """
    Agent 3 – Portfolio Advisor.

    Takes an AnalysisReport + user portfolio and produces a
    PersonalizedInsight with impact assessment and educational suggestions.
    """
    llm = get_llm_client()

    # Default demo portfolio if none provided
    if not user_portfolio:
        user_portfolio = [
            {"instrument": "EUR/USD", "direction": "long", "size": 1.0, "entry_price": 1.0830, "pnl": 12.50},
            {"instrument": "BTC/USD", "direction": "long", "size": 0.1, "entry_price": 95000, "pnl": 250.00},
            {"instrument": "GOLD", "direction": "short", "size": 0.5, "entry_price": 2860, "pnl": -15.00},
        ]

    # Find positions related to the event instrument
    affected = [
        p for p in user_portfolio
        if p.get("instrument", "").upper() == report.instrument.upper()
        or report.instrument.upper() in p.get("instrument", "").upper()
    ]

    portfolio_context = json.dumps(user_portfolio, indent=2)
    affected_context = json.dumps(affected, indent=2) if affected else "No directly affected positions."

    prompt = f"""Market Analysis Report:
- Instrument: {report.instrument}
- Event: {report.event_summary}
- Root Causes: {'; '.join(report.root_causes)}
- Sentiment: {report.sentiment} (score: {report.sentiment_score})
- Key Data Points: {'; '.join(report.key_data_points)}

User Portfolio:
{portfolio_context}

Directly Affected Positions:
{affected_context}

Provide a personalised impact assessment. Return JSON only."""

    try:
        response = llm.simple_chat(
            system_prompt=_ADVISOR_SYSTEM,
            user_message=prompt,
            temperature=0.5,
            max_tokens=500,
        )
        parsed = _parse_json(response)

        return PersonalizedInsight(
            instrument=report.instrument,
            impact_summary=parsed.get("impact_summary", "Impact assessment unavailable."),
            affected_positions=affected,
            risk_assessment=parsed.get("risk_assessment", "medium"),
            suggestions=parsed.get("suggestions", ["Review your position sizing."]),
        )
    except Exception as exc:
        print(f"[PortfolioAdvisor] Error: {exc}")
        return PersonalizedInsight(
            instrument=report.instrument,
            impact_summary=f"The {report.instrument} event may relate to your current positions.",
            affected_positions=affected,
            risk_assessment="medium",
            suggestions=["Consider reviewing your exposure to this instrument."],
        )


# ─── Agent 4: Content Creator ─────────────────────────────────────────

_CONTENT_SYSTEM = f"""You are TradeIQ's Social Content Creator.
Create English Bluesky market commentary posts.

{MASTER_COMPLIANCE_RULES}

Requirements:
- Each post MUST be ≤ 300 characters
- Include specific data points (prices, percentages)
- Use 1-2 relevant emojis
- Include 2-3 hashtags
- End with "📊 Analysis by TradeIQ | Not financial advice"
- NEVER predict or recommend

Output a JSON object:
{{
  "post": "<English post ≤ 300 chars>",
  "hashtags": ["#tag1", "#tag2"],
  "data_points": ["point1", "point2"]
}}
"""


def content_creator_generate(
    report: AnalysisReport,
    insight: Optional[PersonalizedInsight] = None,
) -> MarketCommentary:
    """
    Agent 4 – Content Creator.

    Takes an AnalysisReport (and optionally a PersonalizedInsight)
    and produces English Bluesky market commentary posts.
    """
    llm = get_llm_client()

    insight_context = ""
    if insight:
        insight_context = f"""
Personalised Context:
- Impact: {insight.impact_summary}
- Risk: {insight.risk_assessment}
"""

    prompt = f"""Create Bluesky market commentary post based on:

Analysis Report:
- Instrument: {report.instrument}
- Event: {report.event_summary}
- Root Causes: {'; '.join(report.root_causes[:3])}
- Sentiment: {report.sentiment} (score: {report.sentiment_score})
- Key Data: {'; '.join(report.key_data_points[:3])}
- Sources: {', '.join(s.get('source', '') for s in report.news_sources[:3])}
{insight_context}

Generate an English Bluesky post ≤ 300 chars. Return JSON only."""

    compliance_tag = "📊 Analysis by TradeIQ | Not financial advice"

    try:
        response = llm.simple_chat(
            system_prompt=_CONTENT_SYSTEM,
            user_message=prompt,
            temperature=0.7,
            max_tokens=500,
        )
        parsed = _parse_json(response)

        post = parsed.get("post", "")

        # Ensure compliance tag (check core text without emoji)
        if "Analysis by TradeIQ" not in post:
            if len(post) + len(compliance_tag) + 2 <= 300:
                post = post.rstrip() + f"\n{compliance_tag}"

        # Truncate to 300 chars (Bluesky limit)
        if len(post) > 300:
            post = post[:297] + "..."

        return MarketCommentary(
            post=post,
            hashtags=parsed.get("hashtags", ["#TradeIQ", "#Markets"]),
            data_points=parsed.get("data_points", []),
        )
    except Exception as exc:
        print(f"[ContentCreator] Error: {exc}")
        return MarketCommentary(
            post=f"📊 {report.instrument} moved {report.sentiment}. {compliance_tag}",
            hashtags=["#TradeIQ", "#Markets"],
            data_points=[report.event_summary],
        )


# ─── Bluesky Publisher ────────────────────────────────────────────────

def publish_to_bluesky(commentary: MarketCommentary) -> Dict[str, Any]:
    """
    Publish a MarketCommentary post to Bluesky via AT Protocol.

    Returns dict with published/bluesky_uri/bluesky_url fields.
    """
    from content.bluesky import BlueskyPublisher

    publisher = BlueskyPublisher()
    result = publisher.post(commentary.post)

    return {
        "published": True,
        "bluesky_uri": result.get("uri", ""),
        "bluesky_url": result.get("url", ""),
    }


# ─── Pipeline Orchestrator ────────────────────────────────────────────

def run_pipeline(
    instruments: Optional[List[str]] = None,
    custom_event: Optional[Dict[str, Any]] = None,
    user_portfolio: Optional[List[Dict[str, Any]]] = None,
    skip_content: bool = False,
) -> PipelineResult:
    """
    Run the full Agent Team pipeline:
      Monitor → Analyst → Advisor → Content Creator

    Args:
        instruments: Instruments to scan (default: major pairs)
        custom_event: Manual event trigger (bypasses monitor scan)
        user_portfolio: User positions for personalised insight
        skip_content: If True, skip content generation step

    Returns:
        PipelineResult with all stages' outputs
    """
    result = PipelineResult(status="in_progress")

    # ── Stage 1: Market Monitor ──
    try:
        event = market_monitor_detect(
            instruments=instruments,
            custom_event=custom_event,
        )
        if event is None:
            result.status = "no_event"
            result.errors.append("No significant volatility detected.")
            result.pipeline_finished_at = datetime.now().isoformat()
            return result

        result.volatility_event = asdict(event)
    except Exception as exc:
        result.status = "error"
        result.errors.append(f"Monitor error: {exc}")
        result.pipeline_finished_at = datetime.now().isoformat()
        return result

    # ── Stage 2: Analyst ──
    try:
        report = analyst_analyze(event)
        result.analysis_report = asdict(report)
    except Exception as exc:
        result.status = "partial"
        result.errors.append(f"Analyst error: {exc}")
        result.pipeline_finished_at = datetime.now().isoformat()
        return result

    # ── Stage 3: Portfolio Advisor ──
    try:
        insight = portfolio_advisor_interpret(report, user_portfolio)
        result.personalized_insight = asdict(insight)
    except Exception as exc:
        result.status = "partial"
        result.errors.append(f"Advisor error: {exc}")
        # Continue to content even if advisor fails
        insight = None

    # ── Stage 4: Content Creator ──
    if not skip_content:
        try:
            commentary = content_creator_generate(report, insight)
            result.market_commentary = asdict(commentary)
        except Exception as exc:
            result.status = "partial"
            result.errors.append(f"Content error: {exc}")

    # ── Stage 5: Publish to Bluesky ──
    if not skip_content and result.market_commentary:
        try:
            publish_result = publish_to_bluesky(commentary)
            result.market_commentary.update(publish_result)
        except Exception as exc:
            result.errors.append(f"Publish error: {exc}")

    # Finalise
    if not result.errors:
        result.status = "success"
    elif result.analysis_report and result.market_commentary:
        result.status = "success"  # all critical stages passed
    else:
        result.status = "partial"

    result.pipeline_finished_at = datetime.now().isoformat()
    return result


# ─── Helpers ──────────────────────────────────────────────────────────

def _parse_json(text: str) -> Dict[str, Any]:
    """Parse JSON from LLM response, stripping markdown fences."""
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned.split("```", 1)[1].split("```", 1)[0].strip()
    return json.loads(cleaned)
