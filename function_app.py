import json
import logging
import azure.functions as func
from waves import plan_waves, to_mermaid

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="plan_waves", methods=["POST"])
def plan_waves_api(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        deps = body["apps"]
        if not isinstance(deps, dict):
            raise TypeError
    except (ValueError, KeyError, TypeError):
        return func.HttpResponse(
            json.dumps({"error": "Send JSON like {\"apps\": {\"web\": [\"api\"], \"api\": []}}"}),
            status_code=400,
            mimetype="application/json",
        )

    try:
        waves = plan_waves(deps)
    except ValueError as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}), status_code=422, mimetype="application/json"
        )

    logging.info("Planned %d waves for %d apps", len(waves), len(deps))
    return func.HttpResponse(
        json.dumps({"waves": waves, "mermaid": to_mermaid(deps)}),
        mimetype="application/json",
    )
