# MTProto Auto Proxies ⚡

Automated Telegram MTProto proxy scraper and real-time feed repository. Scrapes verified proxies from live Telegram channels (such as [ProxyMTProto](https://t.me/s/ProxyMTProto)) every 2 hours via GitHub Actions.

---

## 📡 Live Raw Proxy Feed

You can import or subscribe to the latest auto-updated proxy list directly using this permanent Raw GitHub URL:

```text
https://raw.githubusercontent.com/moshraheem-sudo/mtproto-auto-proxies/main/proxies.txt
```

---

## ⚙️ How It Works

1. **GitHub Actions Cron Automation:** Runs every 2 hours (`0 */2 * * *`) on GitHub's cloud runners.
2. **HTML & Regex Scraper (`scraper.py`):** Fetches the latest published MTProto proxy configurations.
3. **Canonical Deduplication:** Normalizes `server`, `port`, and `secret` parameters across `tg://proxy` and `https://t.me/proxy` schemes to eliminate any duplicates.
4. **Seamless Integration:** Serves as a real-time fallback and secondary upstream source for [MTProxy Desk](https://github.com/moshraheem-sudo/MTProxy-Desk).

---

## 👨‍💻 Developer & Maintainer

- **Developer:** Mohammed Shaheed Al-Aajeebi (محمد شهيد الاعاجيبي)
- **Repository:** [moshraheem-sudo/mtproto-auto-proxies](https://github.com/moshraheem-sudo/mtproto-auto-proxies)
- **Companion Application:** [MTProxy Desk – Telegram Proxy Manager](https://github.com/moshraheem-sudo/MTProxy-Desk)
