# Scenario switching endpoint - loads fixture to reset demo state
import json
import os
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# Map scenario name to fixture filename (without path)
FIXTURE_MAP = {
    "revenge_trading": "demo_revenge_trading.json",
    "overtrading": "demo_overtrading.json",
    "loss_chasing": "demo_loss_chasing.json",
    "healthy_session": "demo_healthy_session.json",
}


@method_decorator(csrf_exempt, name="dispatch")
class LoadScenarioView(View):
    """
    POST /api/demo/load-scenario/
    Body: {"scenario": "revenge_trading" | "overtrading" | "loss_chasing" | "healthy_session"}
    Loads the corresponding fixture to reset demo state.
    """

    def post(self, request):
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        scenario = body.get("scenario")
        if not scenario or scenario not in FIXTURE_MAP:
            return JsonResponse({
                "error": "scenario required",
                "allowed": list(FIXTURE_MAP.keys()),
            }, status=400)
        fixture_name = FIXTURE_MAP[scenario]
        # Resolve path: backend/fixtures/
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fixture_path = os.path.join(base, "fixtures", fixture_name)
        if not os.path.isfile(fixture_path):
            return JsonResponse({"error": f"Fixture not found: {fixture_name}"}, status=404)
        # Load fixture via Django's loaddata (subprocess) or parse and insert
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        try:
            call_command("loaddata", fixture_name, verbosity=0, stdout=out)
        except Exception as e:
            return JsonResponse({"error": str(e), "scenario": scenario}, status=500)
        return JsonResponse({
            "status": "loaded",
            "scenario": scenario,
            "fixture": fixture_name,
        })
