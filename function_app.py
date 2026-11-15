import json
import logging
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


def plan_waves(deps):
    """Group apps into migration waves. Raises ValueError on a cycle."""
    # Treat dependencies that are not listed as apps in their own right
    all_apps = set(deps)
    for d in deps.values():
        all_apps.update(d)
    remaining = {a: set(deps.get(a, [])) for a in all_apps}

    waves = []
    while remaining:
        ready = sorted(a for a, d in remaining.items() if not d)
        if not ready:
            raise ValueError(f"Cycle detected among: {sorted(remaining)}")
        waves.append(ready)
        for a in ready:
            del remaining[a]
        for d in remaining.values():
            d.difference_update(ready)
    return waves


def to_mermaid(deps):
    """Build a Mermaid flowchart: arrow points from dependency to dependent."""
    lines = ["graph LR"]
    for app_name, needs in deps.items():
        if not needs:
            lines.append(f"    {app_name}")
        for n in needs:
            lines.append(f"    {n} --> {app_name}")
    return "\n".join(lines)


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
