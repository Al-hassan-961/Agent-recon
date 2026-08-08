#!/usr/bin/env python3
import argparse
import asyncio
import os
from core.engine import OSINTEngine
from modules import notifications

async def main():
    parser = argparse.ArgumentParser(description="Omega-OSINT v2.0 - Recursive Recon Engine")
    parser.add_argument("-t", "--target", required=True, help="Username, email, domain, or IP")
    parser.add_argument("--nmap", action="store_true", help="Enable nmap scanning (requires nmap)")
    parser.add_argument("--notify", action="store_true", help="Send results via Telegram/Discord")
    args = parser.parse_args()

    if args.nmap:
        import config
        config.ENABLE_NMAP = True

    os.makedirs("data", exist_ok=True)

    engine = OSINTEngine()
    discovered, graph = await engine.run(args.target)

    if args.notify:
        msg = f"Omega-OSINT scan complete for {args.target}\n"
        msg += f"Found: {len(discovered['usernames'])} usernames, {len(discovered['emails'])} emails, {len(discovered['domains'])} domains\n"
        msg += f"Graph: data/graph_{args.target}.html"
        await notifications.send_telegram(msg)
        await notifications.send_discord(msg)

if __name__ == "__main__":
    asyncio.run(main())
