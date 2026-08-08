import hashlib
import aiohttp
import requests
from config import TIMEOUT

async def hibp_check_async(email):
    sha1 = hashlib.sha1(email.encode()).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                text = await resp.text()
                for line in text.splitlines():
                    if line.startswith(suffix):
                        count = line.split(':')[1]
                        return True, count
    return False, 0

def get_gravatar_sync(email):
    h = hashlib.md5(email.lower().encode()).hexdigest()
    url = f"https://www.gravatar.com/avatar/{h}?d=404"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return url
    except:
        pass
    return None

async def dehashed_lookup(email):
    # Placeholder – requires paid API; implement if you have credentials
    return None
