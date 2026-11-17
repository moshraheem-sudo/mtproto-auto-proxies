#!/usr/bin/env python3
"""
Automated MTProto Proxy Scraper
Scrapes live Telegram MTProto proxies from the official web preview endpoint:
https://t.me/s/ProxyMTProto (with explicit '/s/' for complete web rendering)

Supported extraction mechanisms:
1. Structured message text extraction (Server: / Port: / Secret:)
2. Inline 'Connect' buttons (<a href="tg://proxy?..." or "https://t.me/proxy?...">)
3. Direct protocol links (tg://proxy and https://t.me/proxy)
4. Multi-page traversal with ?before= pagination
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

# 1. Direct proxy link regex
PROXY_LINK_REGEX = re.compile(
    r'(?:tg://proxy\?[^\s"\'<>]+|https?://t\.me/proxy\?[^\s"\'<>]+)',
    re.IGNORECASE
)

# 2. Structured text pattern for Telegram channels:
# Server: ...
# Port: ...
# Secret: ...
STRUCTURED_TEXT_REGEX = re.compile(
    r'(?:Server|سرور):\s*([a-zA-Z0-9\.\-_]+)[\s\S]*?(?:Port|پورت):\s*(\d+)[\s\S]*?(?:Secret|سیکرت):\s*([a-zA-Z0-9_\-+=/\s]+?)(?=(?:\r?\n\s*(?:@|Connect|دانلود|Download|http|$))|<)',
    re.IGNORECASE
)

BEFORE_PAGE_REGEX = re.compile(r'/s/ProxyMTProto\?before=(\d+)')

def clean_host(host: str) -> str:
    """Cleans domain or IP host string, stripping trailing dots and brackets."""
    s = host.strip().rstrip('.')
    if s.startswith("http://") or s.startswith("https://"):
        s = urllib.parse.urlparse(s).netloc
    if ':' in s and not s.startswith('['):
        s = s.split(':')[0]
    return s.strip().rstrip('.').lower()

def parse_proxy_params(url: str):
    """Parses server, port, and secret to build a canonical deduplication key."""
    try:
        clean_url = url.replace('&amp;', '&').strip()
        parsed = urllib.parse.urlparse(clean_url)
        qs = urllib.parse.parse_qs(parsed.query)
        raw_server = qs.get('server', [''])[0].strip()
        server = clean_host(raw_server)
        port = qs.get('port', [''])[0].strip()
        secret = qs.get('secret', [''])[0].strip()
        if server and port and secret:
            return (server, port, secret)
    except Exception:
        pass
    return None

def fetch_page(url: str, headers: dict) -> str:
    """Fetches HTML with timeout and fallbacks."""
    if requests is not None:
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code == 200:
                return resp.text
        except Exception as e:
            print(f"requests notice for {url}: {e}")

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

def scrape_channel(channel_url=BASE_CHANNEL_URL, max_pages=4):
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

        # Method 1: Extract structured Server / Port / Secret from message text
        for match in STRUCTURED_TEXT_REGEX.finditer(html):
            raw_srv = match.group(1).strip()
            srv = clean_host(raw_srv)
            port = match.group(2).strip()
            sec = re.sub(r'[\s\r\n\t]+', '', match.group(3).strip())
            key = (srv, port, sec)
            if srv and port and sec and key not in seen_keys:
                seen_keys.add(key)
                constructed_url = f"tg://proxy?server={srv}&port={port}&secret={sec}"
                proxies_found.append(constructed_url)
                page_count += 1

        # Method 2: Parse via BeautifulSoup anchor tags & inline buttons
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

        # Method 3: Regex match for direct proxy URLs in HTML
        matches = PROXY_LINK_REGEX.findall(html)
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
