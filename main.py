import argparse
import asyncio
import os

from config import get_settings
from modules.dork_generator import build_dork_urls, generate_dorks, open_dorks_in_browser
from modules.email_breach import check_breaches
from modules.exif_extractor import extract_exif
from modules.username_checker import check_username
from modules.whois_lookup import lookup_domain
from report.generator import generate_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PhantomTrace OSINT Footprinting Tool")
    parser.add_argument("--username", help="Username to check across platforms")
    parser.add_argument("--email", help="Email address for breach lookup")
    parser.add_argument("--image", help="Image path for EXIF extraction")
    parser.add_argument("--domain", help="Domain for WHOIS lookup")
    parser.add_argument("--dork", help="Target name/domain for Google dorks")
    parser.add_argument("--all", action="store_true", help="Run all available modules")
    parser.add_argument(
        "--open-dorks",
        action="store_true",
        help="Open generated dork URLs in the browser",
    )
    parser.add_argument(
        "--output",
        default=os.path.join("output", "report.html"),
        help="Output HTML report path",
    )
    return parser.parse_args()


def _build_target_name(args: argparse.Namespace) -> str:
    """Derive a human-readable target name from the provided CLI arguments."""
    parts = []
    if args.username:
        parts.append(args.username)
    if args.email:
        parts.append(args.email)
    if args.domain:
        parts.append(args.domain)
    if args.dork:
        parts.append(args.dork)
    return ", ".join(parts) if parts else "Unknown Target"


def main() -> None:
    args = parse_args()
    settings = get_settings()

    results = {
        "username_results": None,
        "email_results": None,
        "exif_results": None,
        "whois_results": None,
        "dork_results": None,
    }

    if args.username:
        results["username_results"] = asyncio.run(check_username(args.username))

    if args.email:
        results["email_results"] = check_breaches(
            args.email, settings.hibp_api_key, settings.hibp_user_agent
        )

    if args.image:
        results["exif_results"] = extract_exif(args.image)

    if args.domain:
        results["whois_results"] = lookup_domain(args.domain)

    if args.dork:
        dorks = generate_dorks(args.dork)
        results["dork_results"] = build_dork_urls(dorks)
        if args.open_dorks:
            open_dorks_in_browser(results["dork_results"])

    if all(value is None for value in results.values()):
        if args.all:
            print("No modules executed. Provide inputs alongside --all.")
        else:
            print("No modules executed. Provide inputs or use --all with parameters.")
        return

    target_name = _build_target_name(args)
    output_path = generate_report(results, args.output, target_name=target_name)
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
