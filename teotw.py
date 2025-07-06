import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import random
import argparse

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36"}
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
        print(f"[DEBUG] {url} -> {response.status_code}")
        if response.status_code in [200, 500]:
            return response.text
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
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
        form_details = {
            "action": urljoin(base_url, form.get("action", "")),
            "method": form.get("method", "get").lower(),
            "inputs": []
        }
        for input_tag in form.find_all("input"):
            form_details["inputs"].append({
                "name": input_tag.get("name"),
                "type": input_tag.get("type", "text")
            })
        forms.append(form_details)
    return forms

def search_sensitive_keywords(page):
    soup = BeautifulSoup(page, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text().lower()
    keywords = ["password", "secret", "pass", "username"]
    found = {}
    for keyword in keywords:
        if keyword in text:
            index = text.find(keyword)
            start = max(index - 30, 0)
            end = min(index + 30 + len(keyword), len(text))
            snippet = soup.get_text()[start:end]
            found[keyword] = re.sub(r'\s+', ' ', snippet.strip())
    return found

def submit_form(session, form, base_url):
    action_url = urljoin(base_url, form.get('action'))
    method = form.get('method', 'get').lower()
    payload = {}
    for field in form.get('inputs', []):
        if field.get('name'):
            payload[field['name']] = 'admin'
    try:
        if method == 'post':
            resp = session.post(action_url, data=payload, headers=headers)
        else:
            resp = session.get(action_url, params=payload, headers=headers)
        return resp
    except Exception as e:
        print(f"[ERROR] Submitting form to {action_url} -> {e}")
        return None

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
            for inp in form["inputs"]:
                print(f"        - name: {inp['name']}, type: {inp['type']}")
            resp = submit_form(session, form, url)
            if resp:
                print(f"      Form submission response code: {resp.status_code}")

    links = extract_links(page, url)
    print(f"  Links Found: {len(links)}")
    for l in links:
        print(f"    - {l}")
    for link in links:
        crawl(link, depth + 1, max_depth)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TEOTW - The Eye Of The Web - Web Crawler & Scanner")
    parser.add_argument("-u", "--url", help="Target URL to scan")
    parser.add_argument("-l", "--list", help="File containing list of URLs to scan")
    args = parser.parse_args()

    print_banner()

    targets = []

    if args.url:
        targets.append(args.url.strip())
    elif args.list:
        try:
            with open(args.list, 'r') as file:
                targets.extend([line.strip() for line in file if line.strip()])
        except Exception as e:
            print(f"[ERROR] Failed to read file: {e}")
            exit(1)
    else:
        print("[-] Please provide a URL (-u) or list of URLs (-l)")
        exit(1)

    for target in targets:
        if not target.startswith(("http://", "https://")):
            target = "http://" + target
        crawl(target)
