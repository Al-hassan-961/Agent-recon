import asyncio
from googlesearch import search
from config import random_ua

async def search_google(query, limit=10):
    loop = asyncio.get_event_loop()
    try:
        results = await loop.run_in_executor(None, lambda: list(search(query, num_results=limit, user_agent=random_ua())))
    except Exception as e:
        print(f"\n[ERROR] Actual crash reason: {e}")
        results = []
    
    return [{"url": r, "snippet": r} for r in results]
