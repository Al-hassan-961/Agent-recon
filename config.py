import os
import random

# ---------- API KEYS (optional) ----------
SHODAN_API = os.getenv("SHODAN_API", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "")
DEHASHED_EMAIL = os.getenv("DEHASHED_EMAIL", "")
DEHASHED_PASS = os.getenv("DEHASHED_PASS", "")

# ---------- TOR / PROXY ----------
USE_TOR = False           # Set to True if you have tor running (pkg install tor)
TOR_PROXY = "socks5://127.0.0.1:9050"

# ---------- USER AGENTS ----------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
]

def random_ua():
    return random.choice(USER_AGENTS)

# ---------- SCAN SETTINGS ----------
MAX_DEPTH = 3
TIMEOUT = 15
CONCURRENT_REQUESTS = 30
ENABLE_NMAP = True
