import asyncio
import re
from tqdm import tqdm
from colorama import Fore, Style
from modules import social_enum, email_intel, domain_recon, dorking
from core.graph import add_relation, generate_graph
import config

class OSINTEngine:
    def __init__(self):
        self.seen_entities = set()
        self.discovered = {
            "usernames": set(),
            "emails": set(),
            "domains": set(),
            "ips": set(),
            "phones": set()
        }
        self.graph_data = []
        self.progress = None

    async def extract_entities_from_text(self, text):
        emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))
        domains = set(re.findall(r'(?:https?://)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})', text))
        phones = set(re.findall(r'\+?\d[\d \-]{8,15}\d', text))
        return emails, domains, phones

    async def scan_username(self, username, depth=0):
        if username in self.seen_entities or depth > config.MAX_DEPTH:
            return
        self.seen_entities.add(username)
        self.discovered["usernames"].add(username)
        self.progress.update(1)
        print(Fore.CYAN + f"[*] Scanning username: {username} (depth {depth})")
        
        profiles = await social_enum.check_all_platforms(username)
        for p in profiles:
            platform = p.get("platform")
            metadata = p.get("metadata", {})
            add_relation(self.graph_data, username, f"has_{platform}_profile", p.get("url", ""))
            bio_text = metadata.get("bio", "") + metadata.get("description", "")
            emails, domains, phones = await self.extract_entities_from_text(bio_text)
            for email in emails:
                add_relation(self.graph_data, username, "email_in_bio", email)
                await self.scan_email(email, depth+1)
            for domain in domains:
                add_relation(self.graph_data, username, "domain_in_bio", domain)
                await self.scan_domain(domain, depth+1)
            for phone in phones:
                add_relation(self.graph_data, username, "phone_in_bio", phone)
        
        # Google dorking
        dork_results = await dorking.search_google(f'"{username}" -site:twitter.com')
        for item in dork_results:
            email_matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', item['snippet'])
            for email in email_matches:
                await self.scan_email(email, depth+1)

    async def scan_email(self, email, depth=0):
        if email in self.seen_entities or depth > config.MAX_DEPTH:
            return
        self.seen_entities.add(email)
        self.discovered["emails"].add(email)
        self.progress.update(1)
        print(Fore.GREEN + f"[+] Scanning email: {email} (depth {depth})")
        
        breach_info = await email_intel.hibp_check_async(email)
        if breach_info[0]:
            add_relation(self.graph_data, email, "breached_in", breach_info[1])
        gravatar = email_intel.get_gravatar_sync(email)
        if gravatar:
            add_relation(self.graph_data, email, "has_gravatar", gravatar)
        if config.DEHASHED_EMAIL:
            dehashed = await email_intel.dehashed_lookup(email)
            if dehashed:
                for entry in dehashed:
                    add_relation(self.graph_data, email, "exposed_on", entry.get("website"))
                    if entry.get("username"):
                        await self.scan_username(entry["username"], depth+1)
        username_candidate = email.split('@')[0]
        await self.scan_username(username_candidate, depth+1)

    async def scan_domain(self, domain, depth=0):
        if domain in self.seen_entities or depth > config.MAX_DEPTH:
            return
        self.seen_entities.add(domain)
        self.discovered["domains"].add(domain)
        self.progress.update(1)
        print(Fore.YELLOW + f"[~] Scanning domain: {domain} (depth {depth})")
        
        whois_data = domain_recon.whois_lookup(domain)
        if whois_data:
            if whois_data.get("registrant_email"):
                await self.scan_email(whois_data["registrant_email"], depth+1)
            if whois_data.get("registrant_org"):
                add_relation(self.graph_data, domain, "registered_by", whois_data["registrant_org"])
        records = domain_recon.dns_enum(domain)
        for record in records.get("A", []):
            self.discovered["ips"].add(record)
            add_relation(self.graph_data, domain, "resolves_to", record)
            if config.ENABLE_NMAP:
                nmap_result = domain_recon.nmap_scan(record)
                if nmap_result:
                    add_relation(self.graph_data, record, "open_ports", nmap_result)
        subdomains = await domain_recon.brute_subdomains(domain)
        for sub in subdomains[:5]:
            add_relation(self.graph_data, domain, "has_subdomain", sub)

    async def run(self, initial_target):
        print(Fore.MAGENTA + "\n[+] Starting recursive OSINT engine...")
        self.progress = tqdm(total=20, desc="Scanning entities", unit="entities")
        if "@" in initial_target:
            await self.scan_email(initial_target, depth=0)
        elif initial_target.replace('.','',1).isdigit() or re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', initial_target):
            if config.ENABLE_NMAP:
                nmap_result = domain_recon.nmap_scan(initial_target)
                add_relation(self.graph_data, "IP", "open_ports", nmap_result)
        elif "." in initial_target and not initial_target.startswith("http"):
            await self.scan_domain(initial_target, depth=0)
        else:
            await self.scan_username(initial_target, depth=0)
        self.progress.close()
        print(Fore.GREEN + f"[✓] Scan complete. Found {len(self.discovered['usernames'])} usernames, {len(self.discovered['emails'])} emails, {len(self.discovered['domains'])} domains.")
        graph_html = generate_graph(self.graph_data, initial_target)
        with open(f"data/graph_{initial_target}.html", "w") as f:
            f.write(graph_html)
        print(Fore.BLUE + f"[✓] Interactive graph saved to data/graph_{initial_target}.html")
        return self.discovered, self.graph_data
