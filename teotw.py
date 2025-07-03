import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import random

headers = {"User-Agent": "Mozilla/5.0 (compatible)"}
visited = set()

ascii_banners = [
    r"""
████████╗███████╗ ██████╗ ████████╗██╗    ██╗██╗
╚══██╔══╝██╔════╝██╔═══██╗╚══██╔══╝██║    ██║██║
   ██║   █████╗  ██║   ██║   ██║   ██║ █╗ ██║██║
   ██║   ██╔══╝  ██║   ██║   ██║   ██║███╗██║██║
   ██║   ███████╗╚██████╔╝   ██║   ╚███╔███╔╝██║
   ╚═╝   ╚══════╝ ╚═════╝    ╚═╝    ╚══╝╚══╝ ╚═╝
        TEOTW - The Eye Of The Web
""",
    r"""
 _______ ______  _____  _______ __          __
|__   __|  ____|/ ____||__   __|\ \        / /
   | |  | |__  | (___     | |    \ \  /\  / / 
   | |  |  __|  \___ \    | |     \ \/  \/ /  
   | |  | |____ ____) |   | |      \  /\  /   
   |_|  |______|_____/    |_|       \/  \/    
          TEOTW - The Eye Of The Web
""",
    r"""
  _______ _______ _______ _______ _     _ 
 (_______|_______|_______|_______|_)   (_)
  _       _____   _____   _____   _______ 
 | |     |  ___) |  ___) |  ___) |  ___  |
 | |_____| |_____| |_____| |_____| |   | |
  \______)_______)_______)_______)_|   |_| 
          TEOTW - The Eye Of The Web
"""
]

def print_banner():
    print(random.choice(ascii_banners))

def fetch_web_page(url):
    try:
        response = requests.get(url, timeout=5, headers=headers)
        if response.status_code in [200, 500]:
            return response.text
    except:
        return None
    return None

def extract_links(page, base_url):
    soup = BeautifulSoup(page, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        link = urljoin(base_url, tag["href"])
        clean_link = link.split('#')[0]
        if urlparse(clean_link).netloc == urlparse(base_url).netloc:
            links.add(clean_link)
    return list(links)

def extract_forms(page, base_url):
    soup = BeautifulSoup(page, "html.parser")
    forms = []
    for form in soup.find_all("form"):
        form_details = {}
        form_details["action"] = urljoin(base_url, form.get("action", ""))
        form_details["method"] = form.get("method", "get").lower()
        inputs = []
        for input_tag in form.find_all("input"):
            input_info = {
                "name": input_tag.get("name"),
                "type": input_tag.get("type", "text")
            }
            inputs.append(input_info)
        form_details["inputs"] = inputs
        forms.append(form_details)
    return forms

def search_sensitive_keywords(page):
    soup = BeautifulSoup(page, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text()
    clean_text = text.lower()
    keywords = ["password", "secret", "pass", "username"]
    found = {}
    for keyword in keywords:
        if keyword in clean_text:
            index = clean_text.find(keyword)
            start = max(index - 30, 0)
            end = min(index + 30 + len(keyword), len(clean_text))
            snippet = text[start:end]
            snippet_n = re.sub(r'\s+', ' ', snippet.strip())
            found[keyword] = snippet_n
    return found

def submit_form(session, form, base_url):
    action_url = urljoin(base_url, form.get('action'))
    method = form.get('method', 'get').lower()
    payload = {}
    for field in form.get('inputs', []):
        name = field.get('name')
        if name:
            payload[name] = 'admin'
    if method == 'post':
        resp = session.post(action_url, data=payload, headers=headers)
    else:
        resp = session.get(action_url, params=payload, headers=headers)
    return resp

def crawl(url, depth=0, max_depth=2):
    if depth > max_depth or url in visited:
        return
    visited.add(url)
    print("\n------------------------------------------------------------")
    print(f"Crawling URL (depth {depth}): {url}")
    page = fetch_web_page(url)
    if not page:
        print("  Failed to fetch content.")
        return

    found_keywords = search_sensitive_keywords(page)
    if found_keywords:
        print("  Sensitive Keywords Found:")
        for k, v in found_keywords.items():
            print(f"    - {k}: {v[:60]}")
    else:
        print("  Sensitive Keywords Found: None")

    forms = extract_forms(page, url)
    print(f"  Forms Found: {len(forms)}")
    with requests.Session() as session:
        for i, form in enumerate(forms, 1):
            print(f"    Form #{i}:")
            print(f"      Action: {form['action']}")
            print(f"      Method: {form['method']}")
            print(f"      Inputs:")
            for inp in form["inputs"]:
                print(f"        - name: {inp['name']}, type: {inp['type']}")
            resp = submit_form(session, form, url)
            print(f"      Form submission response code: {resp.status_code}")

    links = extract_links(page, url)
    print(f"  Links Found: {len(links)}")
    for l in links:
        print(f"    - {l}")
    for link in links:
        crawl(link, depth + 1, max_depth)

if __name__ == "__main__":
    print_banner()
    target = input("Put the target to crawl: ")
    if not target.startswith(("http://", "https://")):
        target = "http://" + target
    crawl(target)
