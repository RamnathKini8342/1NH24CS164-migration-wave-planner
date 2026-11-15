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