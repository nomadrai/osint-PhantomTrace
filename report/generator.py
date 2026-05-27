from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape


def _compute_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """Compute summary statistics from all module results."""
    summary = {
        "modules_run": 0,
        "platforms_checked": 0,
        "profiles_found": 0,
        "breaches_found": 0,
        "dorks_generated": 0,
    }

    if results.get("username_results") is not None:
        summary["modules_run"] += 1
        summary["platforms_checked"] = len(results["username_results"])
        summary["profiles_found"] = sum(
            1 for r in results["username_results"] if r.get("found")
        )

    if results.get("email_results") is not None:
        summary["modules_run"] += 1
        breaches = results["email_results"].get("breaches", [])
        summary["breaches_found"] = len(breaches)

    if results.get("exif_results") is not None:
        summary["modules_run"] += 1

    if results.get("whois_results") is not None:
        summary["modules_run"] += 1

    if results.get("dork_results") is not None:
        summary["modules_run"] += 1
        summary["dorks_generated"] = len(results["dork_results"])

    return summary


def generate_report(
    results: Dict[str, Any],
    output_path: str,
    target_name: Optional[str] = None,
) -> str:
    template_dir = Path(__file__).parent
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("template.html")

    summary = _compute_summary(results)

    rendered = template.render(
        **results,
        target_name=target_name or "Unknown Target",
        summary=summary,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(rendered)
    return output_path
