import asyncio
from typing import Dict, List, Optional

# pyrefly: ignore [missing-import]
import aiohttp


# Each platform defines:
#   name       — display name
#   url        — profile URL with {username} placeholder
#   method     — detection method: "status" (rely on HTTP status code) or "body" (inspect page content)
#   not_found  — list of strings; if ANY appear in the response body, the profile does NOT exist
#   redirect   — if True, a redirect away from the profile URL means not found
PLATFORMS = [
    {
        "name": "GitHub",
        "url": "https://github.com/{username}",
        "method": "status",
    },
    {
        "name": "GitLab",
        "url": "https://gitlab.com/{username}",
        "method": "status",
    },
    {
        "name": "Bitbucket",
        "url": "https://bitbucket.org/{username}",
        "method": "status",
    },
    {
        "name": "Reddit",
        "url": "https://www.reddit.com/user/{username}/about.json",
        "method": "body",
        "not_found": ['"error": 404', "page not found"],
    },
    {
        "name": "Twitter/X",
        "url": "https://x.com/{username}",
        "method": "body",
        "not_found": [
            "Sorry, that page doesn",
            "This account doesn’t exist",
            "Try searching for another.",
        ],
    },
    {
        "name": "Instagram",
        "url": "https://www.instagram.com/{username}/",
        "method": "body",
        "not_found": [
            "Sorry, this page isn",
            "Page Not Found",
            "The link you followed may be broken",
        ],
    },
    {
        "name": "Facebook",
        "url": "https://www.facebook.com/{username}",
        "method": "body",
        "not_found": [
            "The page you requested was not found",
            "This content isn't available at the moment",
            "This content isn",
            "page_not_found",
            "This Page Isn",
        ],
    },
    {
        "name": "LinkedIn",
        "url": "https://www.linkedin.com/in/{username}",
        "method": "body",
        "not_found": [
            "Page not found",
            "This page doesn",
            "profile-not-found",
            "This LinkedIn Page isn",
        ],
    },
    {
        "name": "YouTube",
        "url": "https://www.youtube.com/@{username}",
        "method": "status",
    },
    {
        "name": "TikTok",
        "url": "https://www.tiktok.com/@{username}",
        "method": "body",
        "not_found": [
            "Couldn't find this account",
            "couldn&#x27;t find this account",
            "user-not-found",
        ],
    },
    {
        "name": "Tumblr",
        "url": "https://{username}.tumblr.com",
        "method": "body",
        "not_found": [
            "There's nothing here",
            "not found",
            "Whatever you were looking for doesn",
        ],
    },
    {
        "name": "Medium",
        "url": "https://medium.com/@{username}",
        "method": "status",
    },
    {
        "name": "Dev.to",
        "url": "https://dev.to/{username}",
        "method": "status",
    },
    {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com/user?id={username}",
        "method": "body",
        "not_found": ["No such user."],
    },
    {
        "name": "Keybase",
        "url": "https://keybase.io/{username}",
        "method": "body",
        "not_found": ["Sorry, what you are looking for...it does not exist.",
                      "Oy!"],
    },
    {
        "name": "CodePen",
        "url": "https://codepen.io/{username}",
        "method": "status",
    },
    {
        "name": "Product Hunt",
        "url": "https://www.producthunt.com/@{username}",
        "method": "status",
    },
    {
        "name": "Dribbble",
        "url": "https://dribbble.com/{username}",
        "method": "status",
    },
    {
        "name": "Behance",
        "url": "https://www.behance.net/{username}",
        "method": "status",
    },
    {
        "name": "Vimeo",
        "url": "https://vimeo.com/{username}",
        "method": "status",
    },
    {
        "name": "SoundCloud",
        "url": "https://soundcloud.com/{username}",
        "method": "status",
    },
    {
        "name": "Flickr",
        "url": "https://www.flickr.com/people/{username}",
        "method": "status",
    },
    {
        "name": "DeviantArt",
        "url": "https://www.deviantart.com/{username}",
        "method": "status",
    },
    {
        "name": "Telegram",
        "url": "https://t.me/{username}",
        "method": "body",
        "not_found": [
            "If you have <strong>Telegram</strong>, you can contact",
            "tgme_page_icon",
        ],
        # Telegram returns 200 for both existing and non-existing; non-existing
        # shows a generic "you can contact @username" stub page.  We invert: if
        # these markers are present it means the page is a stub (NOT a real
        # account).  So we treat "not_found" markers specially below.
    },
    {
        "name": "Quora",
        "url": "https://www.quora.com/profile/{username}",
        "method": "body",
        "not_found": [
            "Page Not Found",
            "The page you're looking for doesn",
            "Something went wrong",
        ],
    },
    {
        "name": "VK",
        "url": "https://vk.com/{username}",
        "method": "body",
        "not_found": [
            "Page not found",
            "This user has been deleted",
            "This community has been deleted",
        ],
    },
    {
        "name": "Twitch",
        "url": "https://www.twitch.tv/{username}",
        "method": "body",
        "not_found": [
            "Sorry. Unless you've got a time machine",
            "that page is in another castle",
            "404",
        ],
    },
    {
        "name": "Steam",
        "url": "https://steamcommunity.com/id/{username}",
        "method": "body",
        "not_found": [
            "Error",
            "The specified profile could not be found.",
            "Sorry!",
            "An error was encountered while processing your request:",
            "profile could not be found",
            "error_ctn",
        ],
    },
    {
        "name": "WordPress",
        "url": "https://{username}.wordpress.com",
        "method": "body",
        "not_found": [
            "doesn&#8217;t exist",
            "doesn't exist",
            "This site is no longer available",
        ],
    },
    {
        "name": "Patreon",
        "url": "https://www.patreon.com/{username}",
        "method": "body",
        "not_found": [
            "Sorry, we couldn&#8217;t find that page.",
            "Sorry, we couldn't find that page.",
            "Page not found",
        ],
    },
    {
        "name": "Docker Hub",
        "url": "https://hub.docker.com/u/{username}",
        "method": "status",
    },
    {
        "name": "npm",
        "url": "https://www.npmjs.com/~{username}",
        "method": "status",
    },
    {
        "name": "Unsplash",
        "url": "https://unsplash.com/@{username}",
        "method": "status",
    },
    {
        "name": "LeetCode",
        "url": "https://leetcode.com/u/{username}/",
        "method": "status",
    },
    {
        "name": "HackerRank",
        "url": "https://www.hackerrank.com/profile/{username}",
        "method": "status",
    },
    {
        "name": "Codeforces",
        "url": "https://codeforces.com/profile/{username}",
        "method": "body",
        "not_found": ["User not found", "No such user"],
    },
    {
        "name": "Chess.com",
        "url": "https://www.chess.com/member/{username}",
        "method": "status",
    },
    {
        "name": "Replit",
        "url": "https://replit.com/@{username}",
        "method": "status",
    },
]


def _is_redirect_away(original_url: str, final_url: str) -> bool:
    """Check if the response redirected away from the profile page."""
    # Normalize trailing slashes for comparison
    orig = original_url.rstrip("/").lower()
    final = final_url.rstrip("/").lower()
    # If the final URL is completely different from the original, it was redirected away
    if orig == final:
        return False
    # Some sites redirect profile → login page or homepage when user doesn't exist
    return True


async def _fetch_status(
    session: aiohttp.ClientSession, platform: Dict[str, str], username: str
) -> Dict[str, object]:
    url = platform["url"].format(username=username)
    method = platform.get("method", "status")
    not_found_markers = platform.get("not_found", [])
    status: Optional[int] = None
    found = False

    try:
        async with session.get(url, allow_redirects=True) as response:
            status = response.status

            if status == 404:
                found = False
            elif status >= 400:
                found = False
            elif method == "body" and not_found_markers:
                # Read part of the body to check for "not found" indicators
                # Limit to first 100KB to avoid downloading huge pages
                body_bytes = await response.content.read(102400)
                body = body_bytes.decode("utf-8", errors="ignore").lower()

                # Check if any "not found" marker appears in the body
                page_has_not_found = any(
                    marker.lower() in body for marker in not_found_markers
                )

                if page_has_not_found:
                    found = False
                else:
                    # Also check for redirect: if the site redirected us away
                    # from the profile URL, the profile likely doesn't exist
                    final_url = str(response.url)
                    if _is_redirect_away(url, final_url):
                        found = False
                    else:
                        found = True
            elif method == "status":
                # For status-based detection, also check for redirects
                final_url = str(response.url)
                if _is_redirect_away(url, final_url):
                    found = False
                else:
                    found = True
            else:
                found = True

    except asyncio.TimeoutError:
        status = None
        found = False
    except aiohttp.ClientError:
        status = None
        found = False

    return {
        "platform": platform["name"],
        "url": platform["url"].format(username=username),
        "status": status,
        "found": found,
    }


async def check_username(username: str, timeout: int = 10) -> List[Dict[str, object]]:
    connector = aiohttp.TCPConnector(limit=15)
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    async with aiohttp.ClientSession(
        connector=connector, timeout=client_timeout, headers=headers
    ) as session:
        tasks = [_fetch_status(session, platform, username) for platform in PLATFORMS]
        results = await asyncio.gather(*tasks)
    return list(results)
