import streamlit as st
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
    
    fi = first[0]
    li = last[0]
    f2 = first[:2] if len(first) >= 2 else first 

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
        server.mail('verifier@yourdomain.com') 
        code, message = server.rcpt(email)
        server.quit()
        return "✅ VALID" if code == 250 else "❌ Invalid"
    except Exception:
        return "⚠️ Server Blocked/Timeout"

def is_catch_all(domain):
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    fake_email = f"{random_str}@{domain}"
    status = verify_email(fake_email, domain)
    return "✅ VALID" in status

# ==========================================
# 3. THE BING STEALTH BYPASS SCRAPER
# ==========================================
def search_stealth_for_leader(domain, role, status_placeholder):
    query = f'site:linkedin.com/in "{domain}" "{role}"'
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.bing.com/search?q={encoded_query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
    }
    
    try:
        status_placeholder.info(f"🔎 Engaging Stealth X-Ray for the {role}...")
        time.sleep(1) 
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
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
def find_c_level_and_emails(domain, status_placeholder):
    status_placeholder.info(f"🔍 Stage 1: Scanning {domain} website...")
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
                                    st.write(f"   ✅ Found {job_title} on site: {name}")
            except:
                continue
    except Exception:
        status_placeholder.warning("   ⚠️ Website failed to load. Switching entirely to Stealth X-Ray.")

    status_placeholder.info(f"🔍 Stage 2: Checking Bing/LinkedIn for missing leaders...")
    for kw, job_title in target_titles.items():
        if job_title not in found_leaders:
            xray_name = search_stealth_for_leader(domain, job_title, status_placeholder)
            if xray_name:
                found_leaders[job_title] = {"Name": xray_name, "Direct_Email": None, "Source": "Bing/LinkedIn"}
                st.write(f"   ✅ Found {job_title} via X-Ray: {xray_name}")

    if not found_leaders:
        return [{"Domain": domain, "Title": "None", "Name": "No leaders found", "Email": "N/A", "Status": "N/A"}]

    status_placeholder.info(f"🔍 Stage 3: Verifying MX Server Security for {domain}...")
    catch_all = is_catch_all(domain)
    if catch_all:
        status_placeholder.warning("   ⚠️ WARNING: This server is a 'Catch-All'. It will accept any email address.")
    else:
        status_placeholder.success("   🟢 Server is strict. Email verification will be highly accurate.")

    results = []
    status_placeholder.info(f"🔍 Stage 4: Generating and verifying emails for {len(found_leaders)} leaders...")
    
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
        fallback_email = f"{first}.{last}@{domain}" 
        valid_email_found = False
        
        for email in emails_to_test:
            status = verify_email(email, domain)
            
            if "✅ VALID" in status:
                if catch_all:
                    results.append({"Domain": domain, "Title": title, "Name": name, "Email": fallback_email, "Status": f"⚠️ Catch-All (Pattern Guessed)"})
                    valid_email_found = True
                    st.write(f"   [CATCH-ALL] Best Guess: {fallback_email}")
                    break
                else:
                    results.append({"Domain": domain, "Title": title, "Name": name, "Email": email, "Status": f"✅ Verified SMTP ({data['Source']})"})
                    valid_email_found = True
                    st.write(f"   [SUCCESS] Verified exactly: {email}")
                    break 

        if not valid_email_found:
             results.append({"Domain": domain, "Title": title, "Name": name, "Email": fallback_email, "Status": f"Unverified Pattern ({data['Source']})"})

    return results

# ==========================================
# STREAMLIT UI
# ==========================================
st.set_page_config(page_title="Nexus Lead Finder", page_icon="🔍", layout="wide")

st.title("🔍 Nexus Lead Finder & Verifier (V4)")
st.markdown("Automated B2B Lead Generation and Verification Tool.")

# Create Tabs for the different modes
tab1, tab2, tab3 = st.tabs(["1. Search by Domain", "2. Search by Name", "3. Verify Direct Email"])

with tab1:
    st.header("Search by Domain")
    st.markdown("Finds the entire leadership team for a given company.")
    domain_input = st.text_input("Enter Domain Name (e.g., apple.com)", key="domain_search")
    
    if st.button("Search Domain", type="primary"):
        if domain_input:
            status_placeholder = st.empty()
            with st.spinner("Executing Search..."):
                results = find_c_level_and_emails(domain_input, status_placeholder)
                
            if results:
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Results as CSV",
                    data=csv,
                    file_name=f'{domain_input}_leads.csv',
                    mime='text/csv',
                )
        else:
            st.warning("Please enter a domain.")

with tab2:
    st.header("Search by Name")
    st.markdown("Find and verify an email for a specific person.")
    col1, col2 = st.columns(2)
    with col1:
        first_name_input = st.text_input("First Name")
    with col2:
        last_name_input = st.text_input("Last Name")
    specific_domain_input = st.text_input("Company Domain (e.g., apple.com)")
    
    if st.button("Find Email", type="primary"):
        if first_name_input and last_name_input and specific_domain_input:
            status_placeholder = st.empty()
            with st.spinner("Verifying Patterns..."):
                status_placeholder.info(f"🔍 Checking Server Security for {specific_domain_input}...")
                catch_all = is_catch_all(specific_domain_input)
                
                status_placeholder.info(f"🔍 Generating and verifying patterns...")
                emails_to_test = generate_emails(first_name_input, last_name_input, specific_domain_input)
                
                first = re.sub(r'[^a-zA-Z]', '', first_name_input.lower())
                last = re.sub(r'[^a-zA-Z]', '', last_name_input.lower())
                fallback_email = f"{first}.{last}@{specific_domain_input}"
                
                results = []
                valid_email_found = False
                
                for email in emails_to_test:
                    status = verify_email(email, specific_domain_input)
                    if "✅ VALID" in status:
                        if catch_all:
                            results.append({"Domain": specific_domain_input, "Title": "Targeted Lead", "Name": f"{first_name_input} {last_name_input}", "Email": fallback_email, "Status": "⚠️ Catch-All (Guessed)"})
                            st.write(f"   [CATCH-ALL] Server lies. Best pattern guess: {fallback_email}")
                        else:
                            results.append({"Domain": specific_domain_input, "Title": "Targeted Lead", "Name": f"{first_name_input} {last_name_input}", "Email": email, "Status": "✅ Verified SMTP"})
                            st.write(f"   [SUCCESS] Verified exactly: {email}")
                        valid_email_found = True
                        break
                        
                if not valid_email_found:
                     results.append({"Domain": specific_domain_input, "Title": "Targeted Lead", "Name": f"{first_name_input} {last_name_input}", "Email": fallback_email, "Status": "Unverified Pattern"})
                     
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
        else:
            st.warning("Please fill in all fields.")

with tab3:
    st.header("Verify Direct Email")
    st.markdown("Check if a specific email address is real and active.")
    verify_email_input = st.text_input("Enter Email Address")
    
    if st.button("Verify Email", type="primary"):
        if verify_email_input:
            with st.spinner("Checking Server..."):
                if not re.match(r"[^@]+@[^@]+\.[^@]+", verify_email_input):
                    st.error("❌ Invalid email format.")
                else:
                    domain = verify_email_input.split('@')[1]
                    
                    st.info(f"Checking Server Security for {domain}...")
                    if is_catch_all(domain):
                        st.warning(f"⚠️ [CATCH-ALL] The server for {domain} accepts all emails. Cannot confirm if {verify_email_input} belongs to a real person.")
                        status = "⚠️ Catch-All Server"
                    else:
                        status = verify_email(verify_email_input, domain)
                        if "✅ VALID" in status:
                            st.success(f"✅ [SUCCESS] {verify_email_input} is active and valid!")
                        else:
                            st.error(f"❌ [RESULT] {status}")
                            
                    results = [{"Domain": domain, "Title": "Direct Verifier", "Name": "N/A", "Email": verify_email_input, "Status": status}]
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
        else:
            st.warning("Please enter an email address.")
