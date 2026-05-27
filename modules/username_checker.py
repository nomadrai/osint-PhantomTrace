import asyncio
from typing import Dict, List

import aiohttp


PLATFORMS = [
    {"name": "GitHub", "url": "https://github.com/{username}"},
    {"name": "GitLab", "url": "https://gitlab.com/{username}"},
    {"name": "Bitbucket", "url": "https://bitbucket.org/{username}"},
    {"name": "Reddit", "url": "https://www.reddit.com/user/{username}"},
    {"name": "Twitter/X", "url": "https://x.com/{username}"},
    {"name": "Instagram", "url": "https://www.instagram.com/{username}"},
    {"name": "Facebook", "url": "https://www.facebook.com/{username}"},
    {"name": "LinkedIn", "url": "https://www.linkedin.com/in/{username}"},
    {"name": "YouTube", "url": "https://www.youtube.com/@{username}"},
    {"name": "Twitch", "url": "https://www.twitch.tv/{username}"},
    {"name": "TikTok", "url": "https://www.tiktok.com/@{username}"},
    {"name": "Pinterest", "url": "https://www.pinterest.com/{username}"},
    {"name": "Tumblr", "url": "https://{username}.tumblr.com"},
    {"name": "Medium", "url": "https://medium.com/@{username}"},
    {"name": "Dev.to", "url": "https://dev.to/{username}"},
    {"name": "StackOverflow", "url": "https://stackoverflow.com/users/{username}"},
    {"name": "Hacker News", "url": "https://news.ycombinator.com/user?id={username}"},
    {"name": "Pastebin", "url": "https://pastebin.com/u/{username}"},
    {"name": "Keybase", "url": "https://keybase.io/{username}"},
    {"name": "CodePen", "url": "https://codepen.io/{username}"},
    {"name": "CodeSandbox", "url": "https://codesandbox.io/u/{username}"},
    {"name": "Replit", "url": "https://replit.com/@{username}"},
    {"name": "Kaggle", "url": "https://www.kaggle.com/{username}"},
    {"name": "Product Hunt", "url": "https://www.producthunt.com/@{username}"},
    {"name": "Dribbble", "url": "https://dribbble.com/{username}"},
    {"name": "Behance", "url": "https://www.behance.net/{username}"},
    {"name": "Vimeo", "url": "https://vimeo.com/{username}"},
    {"name": "SoundCloud", "url": "https://soundcloud.com/{username}"},
    {"name": "Flickr", "url": "https://www.flickr.com/people/{username}"},
    {"name": "Goodreads", "url": "https://www.goodreads.com/{username}"},
    {"name": "Steam", "url": "https://steamcommunity.com/id/{username}"},
    {"name": "Roblox", "url": "https://www.roblox.com/user.aspx?username={username}"},
    {"name": "DeviantArt", "url": "https://www.deviantart.com/{username}"},
    {"name": "Etsy", "url": "https://www.etsy.com/people/{username}"},
    {"name": "Telegram", "url": "https://t.me/{username}"},
    {"name": "Quora", "url": "https://www.quora.com/profile/{username}"},
    {"name": "VK", "url": "https://vk.com/{username}"},
    {"name": "Imgur", "url": "https://imgur.com/user/{username}"},
    {"name": "Strava", "url": "https://www.strava.com/athletes/{username}"},
    {"name": "Foursquare", "url": "https://foursquare.com/{username}"},
    {"name": "500px", "url": "https://500px.com/{username}"},
    {"name": "Spotify", "url": "https://open.spotify.com/user/{username}"},
    {"name": "Mixcloud", "url": "https://www.mixcloud.com/{username}"},
    {"name": "WordPress", "url": "https://{username}.wordpress.com"},
    {"name": "Blogger", "url": "https://{username}.blogspot.com"},
    {"name": "Patreon", "url": "https://www.patreon.com/{username}"},
    {"name": "Gitee", "url": "https://gitee.com/{username}"},
    {"name": "SourceForge", "url": "https://sourceforge.net/u/{username}"},
    {"name": "Launchpad", "url": "https://launchpad.net/~{username}"},
    {"name": "PyPI", "url": "https://pypi.org/user/{username}"},
    {"name": "Docker Hub", "url": "https://hub.docker.com/u/{username}"},
    {"name": "npm", "url": "https://www.npmjs.com/~{username}"},
    {"name": "Unsplash", "url": "https://unsplash.com/@{username}"},
    {"name": "LeetCode", "url": "https://leetcode.com/{username}"},
    {"name": "HackerRank", "url": "https://www.hackerrank.com/{username}"},
    {"name": "Codeforces", "url": "https://codeforces.com/profile/{username}"},
    {"name": "StackExchange", "url": "https://stackexchange.com/users/{username}"},
    {"name": "Chess.com", "url": "https://www.chess.com/member/{username}"},
]


async def _fetch_status(
    session: aiohttp.ClientSession, platform: Dict[str, str], username: str
) -> Dict[str, object]:
    url = platform["url"].format(username=username)
    status = None
    try:
        async with session.head(url, allow_redirects=True) as response:
            status = response.status
            if status in {403, 405}:
                async with session.get(url, allow_redirects=True) as get_response:
                    status = get_response.status
    except asyncio.TimeoutError:
        status = None
    except aiohttp.ClientError:
        status = None

    found = status is not None and status < 400 and status != 404
    return {
        "platform": platform["name"],
        "url": url,
        "status": status,
        "found": found,
    }


async def check_username(username: str, timeout: int = 8) -> List[Dict[str, object]]:
    connector = aiohttp.TCPConnector(limit=20)
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    headers = {"User-Agent": "PhantomTrace/1.0"}
    async with aiohttp.ClientSession(
        connector=connector, timeout=client_timeout, headers=headers
    ) as session:
        tasks = [_fetch_status(session, platform, username) for platform in PLATFORMS]
        results = await asyncio.gather(*tasks)
    return results
