import subprocess
import socket
import dns.resolver
import asyncio

def whois_lookup(domain):
    try:
        import whois
        w = whois.whois(domain)
        return {
            "registrar": w.registrar,
            "registrant_email": w.emails if isinstance(w.emails, str) else (w.emails[0] if w.emails else None),
            "registrant_org": w.org,
            "creation_date": str(w.creation_date)
        }
    except:
        try:
            result = subprocess.run(['whois', domain], capture_output=True, text=True, timeout=5)
            for line in result.stdout.splitlines():
                if 'Registrant Email:' in line:
                    email = line.split(':')[1].strip()
                    return {"registrant_email": email}
        except:
            pass
    return {}

def dns_enum(domain):
    records = {"A": [], "MX": [], "NS": [], "TXT": []}
    try:
        for qtype in ['A', 'MX', 'NS', 'TXT']:
            answers = dns.resolver.resolve(domain, qtype)
            for ans in answers:
                records[qtype].append(str(ans))
    except:
        pass
    return records

def nmap_scan(target):
    try:
        result = subprocess.run(['nmap', '-sV', '-O', '-F', target], capture_output=True, text=True, timeout=30)
        open_ports = []
        for line in result.stdout.splitlines():
            if '/tcp' in line and 'open' in line:
                parts = line.split()
                if len(parts) >= 3:
                    open_ports.append(f"{parts[0]} ({parts[2]})")
        return open_ports
    except:
        return None

async def brute_subdomains(domain):
    common = ['www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk', 'ns2',
              'cpanel', 'whm', 'autodiscover', 'autoconfig', 'm', 'imap', 'test', 'ns', 'blog', 'pop3',
              'dev', 'www2', 'admin', 'forum', 'news', 'vpn', 'ns3', 'mail2', 'new', 'mysql', 'old', 'lists',
              'support', 'mobile', 'mx', 'static', 'docs', 'beta', 'shop', 'sql', 'secure', 'demo', 'cp',
              'calendar', 'wiki', 'web', 'media', 'email', 'images', 'img', 'download', 'dns', 'piwik']
    found = []
    for sub in common:
        full = f"{sub}.{domain}"
        try:
            socket.gethostbyname(full)
            found.append(full)
        except:
            pass
    return found
