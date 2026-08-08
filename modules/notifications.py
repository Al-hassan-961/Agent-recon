import aiohttp
import asyncio
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DISCORD_WEBHOOK

async def send_telegram(message):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=data)

async def send_discord(message):
    if DISCORD_WEBHOOK:
        async with aiohttp.ClientSession() as session:
            await session.post(DISCORD_WEBHOOK, json={"content": message})
