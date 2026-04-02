import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import re
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Nexus X-Ray | Lead Generator", page_icon="⚡", layout="centered")

st.title("⚡ Nexus Stealth X-Ray")
st.markdown("Bypass Google CAPTCHAs and safely extract LinkedIn leads using the Bing Stealth Engine.")

# --- USER INPUTS ---
col1, col2 = st.columns(2)
with col1:
    job_title = st.text_input("Job Title*", placeholder="e.g., CEO, Founder, Director")
with col2:
    location = st.text_input("Location", placeholder="e.g., London, New York")

keyword = st.text_input("Industry / Keyword", placeholder="e.g., Software, Real Estate, SaaS")

# --- SCRAPING ENGINE ---
def scrape_bing_xray(job, loc, kw):
    query = f'site:linkedin.com/in "{job}"'
    if loc: query += f' "{loc}"'
    if kw: query += f' "{kw}"'
    
    encoded_query = urllib.parse.quote_plus(query)
    scrape_url = f"https://www.bing.com/search?q={encoded_query}&count=50"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    scraped_data = []
    
    try:
        time.sleep(1) # Human delay
        response = requests.get(scrape_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        search_results = soup.find_all('li', class_='b_algo')
        
        for result in search_results:
            a_tag = result.find('a', href=True)
            if a_tag:
                href = a_tag['href']
                if "linkedin.com/in/" in href and "/dir/" not in href:
                    raw_title = a_tag.get_text(separator=' ', strip=True)
                    clean_title = re.sub(r'\s*[-|]\s*LinkedIn.*$', '', raw_title, flags=re.IGNORECASE)
                    
                    parts = clean_title.split("-")
                    name = parts[0].strip()
                    name = re.sub(r'[^a-zA-Z\s\.\-]', '', name).strip()
                    headline = "-".join(parts[1:]).strip() if len(parts) > 1 else "Profile Found"
                    
                    if len(name) > 3:
                        scraped_data.append({
                            "Name": name,
                            "Headline / Job Title": headline[:100], 
                            "LinkedIn URL": href
                        })
                        
        return scraped_data, query
    except Exception as e:
        st.error(f"Scraping Failed: {e}")
        return [], query

# --- ACTION BUTTON ---
if st.button("🚀 Engage Stealth Scraper", type="primary"):
    if not job_title:
        st.warning("Please enter at least a Job Title.")
    else:
        with st.spinner("Bypassing security matrices and fetching leads..."):
            results, generated_query = scrape_bing_xray(job_title, location, keyword)
            
            st.success(f"Successfully extracted {len(results)} leads!")
            st.info(f"**Search Query Used:** `{generated_query}`")
            
            if results:
                # Display data in a nice web table
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)
                
                # Built-in Streamlit CSV Downloader!
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Leads as CSV",
                    data=csv_data,
                    file_name='nexus_xray_leads.csv',
                    mime='text/csv',
                )