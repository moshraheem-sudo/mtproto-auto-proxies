#!/usr/bin/env python3
"""
Automated MTProto Proxy Scraper
Scrapes live Telegram MTProto proxies from the official web preview endpoint:
https://t.me/s/ProxyMTProto (with '/s/' prefix for full web preview rendering)
Features multi-page pagination, canonical deduplication, and automated updates.
"""

import sys
import os
import re
import urllib.parse
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

BASE_CHANNEL_URL = "https://t.me/s/ProxyMTProto"
OUTPUT_FILE = "proxies.txt"

PROXY_REGEX = re.compile(
    r'(?:tg://proxy\?[^\s"\'<>]+|https?://t\.me/proxy\?[^\s"\'<>]+)',
    re.IGNORECASE
)

BEFORE_PAGE_REGEX = re.compile(r'/s/ProxyMTProto\?before=(\d+)')

def parse_proxy_params(url: str):
    """Parses server, port, and secret to build a canonical deduplication key."""
    try:
        clean_url = url.replace('&amp;', '&').strip()
        parsed = urllib.parse.urlparse(clean_url)
        qs = urllib.parse.parse_qs(parsed.query)
        server = qs.get('server', [''])[0].strip().rstrip('.')
        port = qs.get('port', [''])[0].strip()
        secret = qs.get('secret', [''])[0].strip()
        if server and port and secret:
            return (server.lower(), port, secret)
    except Exception:
        pass
    return None

def fetch_page(url: str, headers: dict) -> str:
    """Fetches HTML from a single URL with timeout and fallback."""
    if requests is not None:
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code == 200:
                return resp.text
        except Exception as e:
            print(f"requests notice for {url}: {e}")

    # Fallback to urllib
    try:
        import urllib.request, ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            return r.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"urllib notice for {url}: {e}")

    return ""

def scrape_channel(channel_url=BASE_CHANNEL_URL, max_pages=3):
    """Scrapes proxies from the web channel, traversing up to max_pages using ?before= pagination."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    proxies_found = []
    seen_keys = set()
    current_url = channel_url

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scrape from: {channel_url}")

    for page_num in range(1, max_pages + 1):
        print(f"Fetching page {page_num}: {current_url}")
        html = fetch_page(current_url, headers)
        if not html:
            print(f"No HTML returned for page {page_num}.")
            break

        page_count = 0

        # 1. Parse via BeautifulSoup anchor tags
        if BeautifulSoup is not None:
            try:
                soup = BeautifulSoup(html, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href'].strip()
                    if 'proxy?' in href and ('t.me/proxy' in href or 'tg://proxy' in href):
                        clean_url = href.replace('&amp;', '&')
                        key = parse_proxy_params(clean_url)
                        if key and key not in seen_keys:
                            seen_keys.add(key)
                            proxies_found.append(clean_url)
                            page_count += 1
            except Exception as e:
                print(f"BeautifulSoup parsing error on page {page_num}: {e}")

        # 2. Complement with Regex
        matches = PROXY_REGEX.findall(html)
        for m in matches:
            clean_url = m.strip().replace('&amp;', '&')
            key = parse_proxy_params(clean_url)
            if key and key not in seen_keys:
                seen_keys.add(key)
                proxies_found.append(clean_url)
                page_count += 1

        print(f"Page {page_num} yielded {page_count} new proxies. Total so far: {len(proxies_found)}")

        # Find pagination link for older messages: e.g. <a class="tme_messages_more" href="/s/ProxyMTProto?before=...">
        before_matches = BEFORE_PAGE_REGEX.findall(html)
        if before_matches:
            next_before = before_matches[0]
            current_url = f"{BASE_CHANNEL_URL}?before={next_before}"
        else:
            break

    print(f"Scraping completed. Found {len(proxies_found)} unique proxies across pages.")
    return proxies_found

def main():
    new_proxies = scrape_channel()

    # Load existing proxies to merge
    existing = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            existing = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    combined = []
    seen = set()

    # New proxies first (freshest)
    for p in new_proxies:
        key = parse_proxy_params(p)
        if key and key not in seen:
            seen.add(key)
            combined.append(p)

    # Retain existing proxies that are unique
    for p in existing:
        key = parse_proxy_params(p)
        if key and key not in seen:
            seen.add(key)
            combined.append(p)

    if combined:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for p in combined:
                f.write(p + '\n')
        print(f"Successfully saved {len(combined)} deduplicated proxies to {OUTPUT_FILE}.")
    else:
        print("No proxies available to save.")

if __name__ == '__main__':
    main()
