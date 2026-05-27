from typing import Dict, List
from urllib.parse import quote_plus
import webbrowser


def generate_dorks(target: str) -> List[str]:
    return [
        f'"{target}" filetype:pdf',
        f'"{target}" filetype:doc OR filetype:docx',
        f'"{target}" filetype:xls OR filetype:xlsx',
        f'"{target}" site:linkedin.com/in',
        f'"{target}" site:github.com',
        f'"{target}" site:pastebin.com',
        f'"{target}" inurl:admin',
        f'"{target}" intext:password',
        f'"{target}" inurl:login',
        f'"{target}" site:twitter.com OR site:x.com',
        f'"{target}" site:facebook.com',
        f'"{target}" site:instagram.com',
        f'"{target}" site:reddit.com',
        f'"{target}" intitle:index.of',
    ]


def build_dork_urls(queries: List[str]) -> List[Dict[str, str]]:
    """Build Google search URLs for each dork query without opening a browser."""
    results = []
    for query in queries:
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        results.append({"query": query, "url": url})
    return results


def open_dorks_in_browser(dork_results: List[Dict[str, str]]) -> None:
    """Open each dork URL in the default browser. Opt-in only."""
    for item in dork_results:
        webbrowser.open(item["url"])
