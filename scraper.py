#!/usr/bin/env python3
"""
Automated MTProto Proxy Scraper
Scrapes live Telegram MTProto proxies from https://t.me/s/ProxyMTProto
Deduplicates while preserving order and updates proxies.txt.
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

TARGET_URL = "https://t.me/s/ProxyMTProto"
OUTPUT_FILE = "proxies.txt"

PROXY_REGEX = re.compile(
    r'(?:tg://proxy\?[^\s"\'<>]+|https?://t\.me/proxy\?[^\s"\'<>]+)',
    re.IGNORECASE
)

def parse_proxy_params(url: str):
    """Parses server, port, and secret to build a canonical deduplication key."""
    try:
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        server = qs.get('server', [''])[0].strip().rstrip('.')
        port = qs.get('port', [''])[0].strip()
        secret = qs.get('secret', [''])[0].strip()
        if server and port and secret:
            return (server.lower(), port, secret)
    except Exception:
        pass
    return None

def fetch_proxies_from_telegram(channel_url=TARGET_URL):
    """Fetches and extracts MTProto proxies from the Telegram web preview."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    proxies_found = []
    seen_keys = set()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching from {channel_url}...")
    html = ""
    if requests is not None:
        try:
            response = requests.get(channel_url, headers=headers, timeout=25)
            response.raise_for_status()
            html = response.text
        except Exception as e:
            print(f"Notice: requests fetch to {channel_url} encountered: {e}")
    
    if not html:
        try:
            import urllib.request, ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(channel_url, headers=headers)
            with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Notice: urllib fallback encountered: {e}")

    if not html:
        print("Could not retrieve HTML from remote endpoint (possible local network block).")
        return proxies_found

    # 1. Parse using BeautifulSoup for anchor tags if available
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
        except Exception as e:
            print(f"BeautifulSoup parsing notice: {e}")

    # 2. Complement with Regex scan across entire raw HTML
    matches = PROXY_REGEX.findall(html)
    for m in matches:
        clean_url = m.strip().replace('&amp;', '&')
        key = parse_proxy_params(clean_url)
        if key and key not in seen_keys:
            seen_keys.add(key)
            proxies_found.append(clean_url)

    print(f"Scraped {len(proxies_found)} unique proxies from {channel_url}.")
    return proxies_found

def main():
    new_proxies = fetch_proxies_from_telegram()

    # Load existing proxies to preserve previous ones or merge
    existing = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            existing = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    combined = []
    seen = set()

    # Add newly scraped proxies first (freshness priority)
    for p in new_proxies:
        key = parse_proxy_params(p)
        if key and key not in seen:
            seen.add(key)
            combined.append(p)

    # Retain previous proxies that are still unique
    for p in existing:
        key = parse_proxy_params(p)
        if key and key not in seen:
            seen.add(key)
            combined.append(p)

    if combined:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for p in combined:
                f.write(p + '\n')
        print(f"Saved {len(combined)} deduplicated proxies to {OUTPUT_FILE}.")
    else:
        print("No proxies available to write.")

if __name__ == '__main__':
    main()
