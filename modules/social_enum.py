import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from config import TIMEOUT, random_ua, TOR_PROXY, USE_TOR

# ----- Metadata Extractors (defined BEFORE the PLATFORMS dict) -----
def extract_twitter(html, username):
    soup = BeautifulSoup(html, 'html.parser')
    desc = soup.find('meta', {'name': 'description'})
    if desc:
        content = desc.get('content', '')
        followers = re.search(r'(\d+[KMB]?) Followers', content)
        return {"bio": content, "followers": followers.group(1) if followers else None}
    return {}

def extract_instagram(html, username):
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and 'edge_followed_by' in script.string:
            import json
            try:
                data = re.search(r'window\._sharedData\s*=\s*({.*?});', script.string)
                if data:
                    json_data = json.loads(data.group(1))
                    user = json_data['entry_data']['ProfilePage'][0]['graphql']['user']
                    return {
                        "bio": user.get('biography', ''),
                        "followers": user.get('edge_followed_by', {}).get('count'),
                        "following": user.get('edge_follow', {}).get('count'),
                        "profile_pic": user.get('profile_pic_url_hd')
                    }
            except:
                pass
    return {}

def extract_github(html, username):
    soup = BeautifulSoup(html, 'html.parser')
    bio = soup.find('div', {'class': 'p-note'})
    return {"bio": bio.text.strip() if bio else ""}

def extract_reddit(html, username):
    soup = BeautifulSoup(html, 'html.parser')
    karma = soup.find('span', {'class': 'karma'})
    return {"karma": karma.text.strip() if karma else None}

def extract_youtube(html, username):
    # placeholder – you can add more sophisticated extraction later
    return {}

def extract_tiktok(html, username):
    return {}

def extract_telegram(html, username):
    return {}

def extract_medium(html, username):
    return {}

# ----- PLATFORMS DICTIONARY (now after function definitions) -----
PLATFORMS = {
    "twitter": ("https://twitter.com/{}", extract_twitter),
    "instagram": ("https://www.instagram.com/{}/", extract_instagram),
    "github": ("https://github.com/{}", extract_github),
    "reddit": ("https://www.reddit.com/user/{}", extract_reddit),
    "youtube": ("https://www.youtube.com/@{}", extract_youtube),
    "tiktok": ("https://www.tiktok.com/@{}", extract_tiktok),
    "telegram": ("https://t.me/{}", extract_telegram),
    "pinterest": ("https://www.pinterest.com/{}/", None),
    "snapchat": ("https://www.snapchat.com/add/{}", None),
    "facebook": ("https://www.facebook.com/{}", None),
    "linkedin": ("https://www.linkedin.com/in/{}", None),
    "medium": ("https://medium.com/@{}", extract_medium),
    "devto": ("https://dev.to/{}", None),
    "keybase": ("https://keybase.io/{}", None),
    "pastebin": ("https://pastebin.com/u/{}", None),
    "hackernews": ("https://news.ycombinator.com/user?id={}", None),
    "mastodon": ("https://mastodon.social/@{}", None),
    "vimeo": ("https://vimeo.com/{}", None),
    "dribbble": ("https://dribbble.com/{}", None),
    "behance": ("https://www.behance.net/{}", None),
    "vkontakte": ("https://vk.com/{}", None),
    "soundcloud": ("https://soundcloud.com/{}", None),
    "twitch": ("https://www.twitch.tv/{}", None),
    "steam": ("https://steamcommunity.com/id/{}", None),
    "spotify": ("https://open.spotify.com/user/{}", None),
    "patreon": ("https://www.patreon.com/{}", None),
    "wordpress": ("https://{}.wordpress.com", None),
    "blogger": ("https://{}.blogspot.com", None),
    "tumblr": ("https://{}.tumblr.com", None),
    "gitlab": ("https://gitlab.com/{}", None),
    "bitbucket": ("https://bitbucket.org/{}/", None),
    "aboutme": ("https://about.me/{}", None),
    "imgur": ("https://imgur.com/user/{}", None),
    "flickr": ("https://www.flickr.com/people/{}", None),
    "quora": ("https://www.quora.com/profile/{}", None),
}

async def check_platform(session, username, platform_name, platform_tuple):
    url_template, extractor = platform_tuple
    url = url_template.format(username)
    headers = {"User-Agent": random_ua()}
    proxy = TOR_PROXY if USE_TOR else None
    try:
        async with session.get(url, headers=headers, proxy=proxy, timeout=TIMEOUT, ssl=False) as resp:
            if resp.status == 200:
                html = await resp.text()
                metadata = extractor(html, username) if extractor else {}
                return {"platform": platform_name, "exists": True, "url": url, "metadata": metadata}
            elif resp.status in (301, 302) and "login" not in resp.headers.get("location", ""):
                html = await resp.text()
                metadata = extractor(html, username) if extractor else {}
                return {"platform": platform_name, "exists": True, "url": url, "metadata": metadata}
            else:
                return {"platform": platform_name, "exists": False}
    except:
        return {"platform": platform_name, "exists": False, "error": True}

async def check_all_platforms(username):
    async with aiohttp.ClientSession() as session:
        tasks = [check_platform(session, username, pname, ptuple) for pname, ptuple in PLATFORMS.items()]
        results = await asyncio.gather(*tasks)
    return [r for r in results if r.get("exists")]
