#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse, parse_qsl, urlencode
import argparse
import re
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

ascii_banners = [
    r"""
  _______ _______ _______ _______ _     _ 
 (_______|_______|_______|_______|_)   (_)
  _       _____   _____   _____   _______ 
 | |     |  ___) |  ___) |  ___) |  ___  |
 | |_____| |_____| |_____| |_____| |   | |
  \______)_______)_______)_______)_|   |_| 
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
    """
]

visited_lock = threading.Lock()
visited = set()
sensitive_keywords = [
    "password", "user", "username", "pass", "admin", "login",
    "email", "secret", "token", "key"
]

def print_banner():
    print(random.choice(ascii_banners))

def normalize_url(url):
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip('/')  # remove trailing slash
    query = urlencode(sorted(parse_qsl(parsed.query)))
    return urlunparse((scheme, netloc, path, '', query, ''))

def is_same_domain(url, base_netloc):
    return urlparse(url).netloc.lower() == base_netloc.lower()

def get_forms(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")
        return soup.find_all("form")
    except Exception:
        return []

def submit_form(form, url):
    try:
        action = form.attrs.get("action", "")
        method = form.attrs.get("method", "get").lower()
        inputs = form.find_all(["input", "textarea", "select"])
        data = {}

        for input_tag in inputs:
            name = input_tag.attrs.get("name")
            input_type = input_tag.attrs.get("type", "text")
            if name:
                data[name] = "test"

        form_url = urljoin(url, action)
        if method == "post":
            res = requests.post(form_url, data=data)
        else:
            res = requests.get(form_url, params=data)

        return res.status_code
    except Exception:
        return None

def crawl(url, depth, max_depth, base_netloc, clear, executor, futures):
    url_norm = normalize_url(url)

    with visited_lock:
        if url_norm in visited or depth > max_depth:
            return
        visited.add(url_norm)

        # Print URL only once here, after adding to visited
        if clear:
            print(url, flush=True)

    try:
        res = requests.get(url, timeout=10)
        if not clear:
            print(f"Crawling URL (depth {depth}): {url}")
            print(f"[DEBUG] {url} -> {res.status_code}")
    except Exception:
        return

    content = res.text
    if not clear:
        found_sensitive = []
        for keyword in sensitive_keywords:
            if re.search(rf"\b{keyword}\b", content, re.IGNORECASE):
                found_sensitive.append(keyword)

        if found_sensitive:
            print("  Sensitive Keywords Found:")
            for keyword in found_sensitive:
                print(f"    - {keyword}")

        forms = get_forms(url)
        if forms:
            print(f"  Forms Found: {len(forms)}")
            for idx, form in enumerate(forms, 1):
                action = form.attrs.get("action", "")
                method = form.attrs.get("method", "get").lower()
                print(f"    Form #{idx}:")
                print(f"      Action: {urljoin(url, action)}")
                print(f"      Method: {method}")

                inputs = form.find_all(["input", "textarea", "select"])
                for input_tag in inputs:
                    name = input_tag.attrs.get("name")
                    input_type = input_tag.attrs.get("type", "text")
                    if name:
                        print(f"        - name: {name}, type: {input_type}")

                status_code = submit_form(form, url)
                if status_code:
                    print(f"      Form submission response code: {status_code}")

    soup = BeautifulSoup(res.content, "html.parser")
    links = soup.find_all("a", href=True)

    for link_tag in links:
        link = urljoin(url, link_tag["href"])
        if is_same_domain(link, base_netloc):
            # Just submit crawl tasks, no printing here
            future = executor.submit(crawl, link, depth + 1, max_depth, base_netloc, clear, executor, futures)
            futures.append(future)
            time.sleep(0.1)

def main():
    parser = argparse.ArgumentParser(description="TEOTW - The Eye Of The Web")
    parser.add_argument("-u", "--url", help="Target URL", required=True)
    parser.add_argument("-d", "--depth", help="Crawling depth", type=int, default=2)
    parser.add_argument("--clear", help="Clear output mode (URLs only)", action="store_true")
    parser.add_argument("-p", "--processors", help="Number of processors (threads) to use", type=int, default=1)
    parser.add_argument("-t", "--test", help="Test flag", action="store_true")
    args = parser.parse_args()

    print_banner()
    print("\n" + "-" * 60)
    print(f"Crawling URL: {args.url}")
    print(f"Processors set to: {args.processors}")
    if args.test:
        print("Test flag is ON")

    base_netloc = urlparse(args.url).netloc

    with ThreadPoolExecutor(max_workers=args.processors) as executor:
        futures = []
        crawl(args.url, 0, args.depth, base_netloc, args.clear, executor, futures)
        for future in as_completed(futures):
            pass  # wait for all threads

if __name__ == "__main__":
    main()
