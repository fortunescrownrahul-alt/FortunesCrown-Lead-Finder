import requests
from bs4 import BeautifulSoup
import re
import smtplib
import dns.resolver
import socket
import csv  
import os   
import urllib.parse
import time
import random
import string
import pandas as pd  # For the beautiful terminal tables!

# ==========================================
# 1. GENERATE ALL 35+ EMAIL PATTERNS
# ==========================================
def generate_emails(first_name, last_name, domain):
    first = re.sub(r'[^a-zA-Z]', '', first_name.lower())
    last = re.sub(r'[^a-zA-Z]', '', last_name.lower())
    
    if not first or not last: 
        return []
    
    fi = first[0] # First Initial
    li = last[0]  # Last Initial
    f2 = first[:2] if len(first) >= 2 else first # First two letters (for special corporate formats)

    # All 34 Permutations + Special Formats
    return [
        f"{first}@{domain}",
        f"{last}@{domain}",
        f"{first}{last}@{domain}",
        f"{first}.{last}@{domain}",
        f"{fi}{last}@{domain}",
        f"{fi}.{last}@{domain}",
        f"{f2}{last}@{domain}",  # The special format
        f"{first}{li}@{domain}",
        f"{first}.{li}@{domain}",
        f"{fi}{li}@{domain}",
        f"{fi}.{li}@{domain}",
        f"{last}{first}@{domain}",
        f"{last}.{first}@{domain}",
        f"{last}{fi}@{domain}",
        f"{last}.{fi}@{domain}",
        f"{li}{first}@{domain}",
        f"{li}.{first}@{domain}",
        f"{li}{fi}@{domain}",
        f"{li}.{fi}@{domain}",
        f"{first}-{last}@{domain}",
        f"{fi}-{last}@{domain}",
        f"{first}-{li}@{domain}",
        f"{fi}-{li}@{domain}",
        f"{last}-{first}@{domain}",
        f"{last}-{fi}@{domain}",
        f"{li}-{first}@{domain}",
        f"{li}-{fi}@{domain}",
        f"{first}_{last}@{domain}",
        f"{fi}_{last}@{domain}",
        f"{first}_{li}@{domain}",
        f"{fi}_{li}@{domain}",
        f"{last}_{first}@{domain}",
        f"{last}_{fi}@{domain}",
        f"{li}_{first}@{domain}",
        f"{li}_{fi}@{domain}"
    ]

# ==========================================
# 2. ADVANCED SMTP VERIFIER (WITH CATCH-ALL DETECTION)
# ==========================================
def verify_email(email, domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
    except Exception:
        return "❌ Failed (No MX)"

    try:
        server = smtplib.SMTP(timeout=3)
        server.connect(mx_record, 25)
        server.helo(socket.getfqdn())
        server.mail('verifier@yourdomain.com') # Generic sender
        code, message = server.rcpt(email)
        server.quit()
        return "✅ VALID" if code == 250 else "❌ Invalid"
    except Exception:
        return "⚠️ Server Blocked/Timeout"

def is_catch_all(domain):
    """Pings a gibberish email to see if the server lies and accepts everything."""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    fake_email = f"{random_str}@{domain}"
    status = verify_email(fake_email, domain)
    return "✅ VALID" in status

# ==========================================
# 3. THE BING STEALTH BYPASS SCRAPER
# ==========================================
def search_stealth_for_leader(domain, role):
    query = f'site:linkedin.com/in "{domain}" "{role}"'
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.bing.com/search?q={encoded_query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
    }
    
    try:
        print(f"   🔎 Website hidden. Engaging Stealth X-Ray for the {role}...")
        time.sleep(1) # Human delay
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Parse Bing results
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if "linkedin.com/in/" in href and "/dir/" not in href:
                raw_title = a_tag.get_text(separator=' ', strip=True)
                clean_title = re.sub(r'\s*[-|]\s*LinkedIn.*$', '', raw_title, flags=re.IGNORECASE)
                parts = clean_title.split("-")
                if parts:
                    name = parts[0].strip()
                    name = re.sub(r'[^a-zA-Z\s\.\-]', '', name).strip()
                    if len(name.split()) >= 2:
                        return name
    except Exception:
        pass
    return None

# ==========================================
# 4. FULL AUTOMATIC SCRAPER ENGINE
# ==========================================
def find_c_level_and_emails(domain):
    print(f"\n🔍 Stage 1: Scanning {domain} website...")
    start_url = f"https://{domain}" if not domain.startswith('http') else domain
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    target_titles = {
        'ceo': 'CEO',
