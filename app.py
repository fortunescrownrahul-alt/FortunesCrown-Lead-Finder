import requests
from bs4 import BeautifulSoup
import re
import smtplib
import dns.resolver
import socket
import urllib.parse
import time
import random
import string
import pandas as pd

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
        f"{first}@{domain}", f"{last}@{domain}", f"{first}{last}@{domain}",
        f"{first}.{last}@{domain}", f"{fi}{last}@{domain}", f"{fi}.{last}@{domain}",
        f"{f2}{last}@{domain}", f"{first}{li}@{domain}", f"{first}.{li}@{domain}",
        f"{fi}{li}@{domain}", f"{fi}.{li}@{domain}", f"{last}{first}@{domain}",
        f"{last}.{first}@{domain}", f"{last}{fi}@{domain}", f"{last}.{fi}@{domain}",
        f"{li}{first}@{domain}", f"{li}.{first}@{domain}", f"{li}{fi}@{domain}",
        f"{li}.{fi}@{domain}", f"{first}-{last}@{domain}", f"{fi}-{last}@{domain}",
        f"{first}-{li}@{domain}", f"{fi}-{li}@{domain}", f"{last}-{first}@{domain}",
        f"{last}-{fi}@{domain}", f"{li}-{first}@{domain}", f"{li}-{fi}@{domain}",
        f"{first}_{last}@{domain}", f"{fi}_{last}@{domain}", f"{first}_{li}@{domain}",
        f"{fi}_{li}@{domain}", f"{last}_{first}@{domain}", f"{last}_{fi}@{domain}",
        f"{li}_{first}@{domain}", f"{li}_{fi}@{domain}"
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
        'ceo': 'CEO', 'cto': 'CTO', 'cfo': 'CFO', 'coo': 'COO', 'cmo': 'CMO',
        'managing director': 'Managing Director', 'owner': 'Owner', 'founder': 'Founder',
    }
    
    found_leaders = {}
    junk_words = ['cookie', 'skip', 'accept', 'menu', 'login', 'search', 'privacy', 'rights', 'reserved', 'profile']

    try:
        response = requests.get(start_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = {start_url}
        for a in soup.find_all('a', href=True):
            if any(kw in a['href'].lower() for kw in ['about', 'team', 'leadership', 'board', 'management']):
                links.add(urllib.parse.urljoin(start_url, a['href']))

        for page in list(links)[:3]:
            try:
                res = requests.get(page, headers=headers, timeout=5)
                page_soup = BeautifulSoup(res.text, 'html.parser')
                for script in page_soup(["script", "style", "nav", "footer"]): script.extract()
                text_nodes = list(page_soup.stripped_strings)
                
                for i, text_node in enumerate(text_nodes):
                    lower_text = text_node.lower()
                    for kw, job_title in target_titles.items():
                        if kw in lower_text and job_title not in found_leaders:
                            surrounding_text = " ".join(text_nodes[max(0, i-3) : i+4])
                            words = re.findall(r'\b[A-Z][a-z]+\b', surrounding_text)
                            direct_email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', surrounding_text)
                            direct_email = direct_email_match.group(0) if direct_email_match else None

                            if len(words) >= 2:
                                name = f"{words[0]} {words[1]}"
                                if not any(junk in name.lower() for junk in junk_words) and len(name) < 25:
                                    found_leaders[job_title] = {"Name": name, "Direct_Email": direct_email, "Source": "Website"}
                                    print(f"   ✅ Found {job_title} on site: {name}")
            except:
                continue
    except Exception:
        print("   ⚠️ Website failed to load. Switching entirely to Stealth X-Ray.")

    print(f"\n🔍 Stage 2: Checking Bing/LinkedIn for missing leaders...")
    for kw, job_title in target_titles.items():
        if job_title not in found_leaders:
            xray_name = search_stealth_for_leader(domain, job_title)
            if xray_name:
                found_leaders[job_title] = {"Name": xray_name, "Direct_Email": None, "Source": "Bing/LinkedIn"}
                print(f"   ✅ Found {job_title} via X-Ray: {xray_name}")

    if not found_leaders:
        return [{"Domain": domain, "Title": "None", "Name": "No leaders found", "Email": "N/A", "Status": "N/A"}]

    print(f"\n🔍 Stage 3: Verifying MX Server Security for {domain}...")
    catch_all = is_catch_all(domain)
    if catch_all:
        print("   ⚠️ WARNING: This server is a 'Catch-All'. It will accept any email address.")
    else:
        print("   🟢 Server is strict. Email verification will be highly accurate.")

    results = []
    print(f"\n🔍 Stage 4: Generating and verifying emails for {len(found_leaders)} leaders...\n")
    
    for title, data in found_leaders.items():
        name = data['Name']
        direct_email = data['Direct_Email']
        
        if direct_email:
            results.append({"Domain": domain, "Title": title, "Name": name, "Email": direct_email, "Status": "✅ Direct from Site"})
            continue

        try:
            first = re.sub(r'[^a-zA-Z]', '', name.split(' ')[0].lower())
            last = re.sub(r'[^a-zA-Z]', '', name.split(' ')[-1].lower())
        except:
            continue
            
        emails_to_test = generate_emails(first, last, domain)
        
        # Explicitly declare fallback as the most common format in the world
        fallback_email = f"{first}.{last}@{domain}" 
        valid_email_found = False
        
        for email in emails_to_test:
            status = verify_email(email, domain)
            
            if "✅ VALID" in status:
                if catch_all:
                    results.append({"Domain": domain, "Title": title, "Name": name, "Email": fallback_email, "Status": f"⚠️ Catch-All (Pattern Guessed)"})
                    valid_email_found = True
                    print(f"   [CATCH-ALL] Best Guess: {fallback_email}")
                    break
                else:
                    results.append({"Domain": domain, "Title": title, "Name": name, "Email": email, "Status": f"✅ Verified SMTP ({data['Source']})"})
                    valid_email_found = True
                    print(f"   [SUCCESS] Verified exactly: {email}")
                    break 

        if not valid_email_found:
             results.append({"Domain": domain, "Title": title, "Name": name, "Email": fallback_email, "Status": f"Unverified Pattern ({data['Source']})"})

    return results

# ==========================================
# 5. SPECIFIC PERSON VERIFIER
# ==========================================
def verify_specific_person(first_name, last_name, domain):
    print(f"\n🔍 Checking Server Security for {domain}...")
    catch_all = is_catch_all(domain)
    
    print(f"🔍 Generating and verifying 35+ patterns for {first_name} {last_name}...")
    emails_to_test = generate_emails(first_name, last_name, domain)
    
    first = re.sub(r'[^a-zA-Z]', '', first_name.lower())
    last = re.sub(r'[^a-zA-Z]', '', last_name.lower())
    fallback_email = f"{first}.{last}@{domain}"
    
    results = []
    valid_email_found = False
    
    for email in emails_to_test:
        status = verify_email(email, domain)
        if "✅ VALID" in status:
            if catch_all:
                results.append({"Domain": domain, "Title": "Targeted Lead", "Name": f"{first_name} {last_name}", "Email": fallback_email, "Status": "⚠️ Catch-All (Guessed)"})
                print(f"   [CATCH-ALL] Server lies. Best pattern guess: {fallback_email}")
            else:
                results.append({"Domain": domain, "Title": "Targeted Lead", "Name": f"{first_name} {last_name}", "Email": email, "Status": "✅ Verified SMTP"})
                print(f"   [SUCCESS] Verified exactly: {email}")
            valid_email_found = True
            break
            
    if not valid_email_found:
         results.append({"Domain": domain, "Title": "Targeted Lead", "Name": f"{first_name} {last_name}", "Email": fallback_email, "Status": "Unverified Pattern"})
         
    return results

# ==========================================
# 6. DIRECT EMAIL VERIFIER
# ==========================================
def verify_direct_email(email):
    print(f"\n🔍 Verifying email address: {email}...")
    
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print("   ❌ Invalid email format.")
        return [{"Domain": "N/A", "Title": "Direct Verifier", "Name": "N/A", "Email": email, "Status": "❌ Invalid Format"}]
    
    domain = email.split('@')[1]
    
    print(f"   Checking Server Security for {domain}...")
    if is_catch_all(domain):
        print(f"   ⚠️ [CATCH-ALL] The server for {domain} accepts all emails. Cannot confirm if {email} belongs to a real person.")
        status = "⚠️ Catch-All Server"
    else:
        status = verify_email(email, domain)
        if "✅ VALID" in status:
            print(f"   [SUCCESS] {email} is active and valid!")
        else:
            print(f"   [RESULT] {status}")
        
    return [{"Domain": domain, "Title": "Direct Verifier", "Name": "N/A", "Email": email, "Status": status}]

# ==========================================
# MAIN MENU UI (CONTINUOUS LOOP)
# ==========================================
if __name__ == "__main__":
    while True:
        print("\n" + "="*50)
        print("    NEXUS LEAD FINDER & VERIFIER (DISPLAY ONLY)")
        print("="*50)
        print("1. Search by Domain (Finds entire leadership team)")
        print("2. Search by Name (Find email for specific person)")
        print("3. Verify Direct Email (Check if an email is real)")
        print("4. Exit Program ❌")
        print("="*50)
        
        choice = input("Enter 1, 2, 3, or 4: ").strip()
        data = []

        if choice == '1':
            target_domain = input("\nEnter domain name (e.g., apple.com): ").strip()
            data = find_c_level_and_emails(target_domain)
            
        elif choice == '2':
            first = input("\nEnter First Name: ").strip()
            last = input("Enter Last Name: ").strip()
            target_domain = input("Enter domain name (e.g., apple.com): ").strip()
            data = verify_specific_person(first, last, target_domain)
            
        elif choice == '3':
            target_email = input("\nEnter the email address to verify: ").strip()
            data = verify_direct_email(target_email)
            
        elif choice == '4':
            print("\n👋 Exiting Nexus Lead Finder. Goodbye!")
            time.sleep(1)
            break
            
        else:
            print("❌ Invalid choice. Please type 1, 2, 3, or 4.")
            time.sleep(1.5)
            continue
        
        # Beautiful Pandas Print Output (No file saving!)
        if data:
            print("\n")
            df = pd.DataFrame(data)
            # index=False hides the row numbers so the table looks much cleaner
            print(df.to_string(index=False)) 
                
            print("\n" + "="*85)
            print(f"   Found {len(data)} records. Displayed above.")
            print("="*85)
                
        # Pauses before resetting the menu
        input("\nPress ENTER to return to the Main Menu...")
