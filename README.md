# MTProto Auto Proxies ⚡ | خادم ومستودع بروكسيات تيليجرام التلقائي

**المستودع الرسمي:** [moshraheem-sudo/mtproto-auto-proxies](https://github.com/moshraheem-sudo/mtproto-auto-proxies)  
**المطور:** محمد شهيد الاعاجيبي (Mohammed Shaheed Al-Aajeebi)  
**المصدر المباشر:** قناة تليجرام العالمية [ProxyMTProto](https://t.me/s/ProxyMTProto) عبر المعاينة السحابية `/s/`  
**دورية التحديث:** سحابياً كل ساعتين عبر GitHub Actions  

---

## 🇸🇦 نبذة عن المستودع (العربية)

مستودع أوتوماتيكي سحابي لجلب واستخراج أحدث وأسرع بروكسيات تيليجرام **MTProto** الحية والواقعية مباشرة من قناة `ProxyMTProto` الرسمية باستخدام المسار الويب الكامل `https://t.me/s/ProxyMTProto`.

### 🛡️ حل مشكلة حظر تيليجرام في العراق والشرق الأوسط:
نظراً لحظر نطاقات `t.me` لدى أغلب مزودي خدمة الإنترنت المحليين في العراق، تعمل **خوادم GitHub Actions في السحابة الدولية** كجسر آمن؛ حيث تقوم بسحب البروكسيات من تليجرام في بيئة مفتوحة عالمياً، وتصفيتها وحفظها في هذا المستودع كملف نصي خام `proxies.txt`، مما يتيح لكافة المستخدمين والبرامج في العراق الوصول الفوري للبروكسيات وتحديثها دون أي حظر أو انقطاع!

### 🌟 أبرز المميزات:
1. **جلب مستمر لأحدث 50+ سيرفر واقعي:** الخوارزمية تتنقل عبر الصفحات السابقة `?before=` وتضمن استخراج أكثر من 50 سيرفر جديد دون إهمال.
2. **استخراج متقدم للمفاتيح:** قراءة البيانات المنظمة (`Server:`, `Port:`, `Secret:`) والروابط المباشرة وأزرار الاتصال التفاعلية.
3. **تحديث تلقائي كل ساعتين:** يتم تشغيل المهام المجدولة تلقائياً وتحديث ملف `proxies.txt` فور توفر بروكسيات جديدة.
4. **تكامل متقدم مع تطبيق سطح المكتب:** يغذي مباشرة تطبيق [MTProxy Desk](https://github.com/moshraheem-sudo/MTProxy-Desk) كمصدر ثانوي متوازي وموثوق مع التكرار الصفري (Deduplication).

---

## 📡 رابط التغذية المباشر الخام (Live Raw Feed)

يمكن لأي برنامج أو تطبيق تليجرام استيراد القائمة الحية مباشرة من الرابط الدائم:
```text
https://raw.githubusercontent.com/moshraheem-sudo/mtproto-auto-proxies/main/proxies.txt
```

---

## 🇬🇧 English Overview

**MTProto Auto Proxies** is a high-performance automated Telegram MTProto proxy scraper running on GitHub Actions. It scrapes live MTProto proxy servers from [ProxyMTProto](https://t.me/s/ProxyMTProto) every 2 hours and publishes clean, deduplicated feeds.

### Key Specifications:
- **Cloud Runner Bypass:** Solves ISP censorship in regions where `t.me` is blocked (e.g. Iraq) by running the scraper in the cloud and publishing via GitHub Raw.
- **Guaranteed 50+ Latest Servers:** Traverses historical pages using `?before=` pagination until at least 50 fresh unique servers are collected.
- **Canonical Deduplication:** Normalizes `(server, port, secret)` keys across `tg://proxy` and `https://t.me/proxy`.
- **Primary Consumer:** Serves as the real-time failover source for [MTProxy Desk](https://github.com/moshraheem-sudo/MTProxy-Desk).

---

## 👨‍💻 المطور / Developer

- **الاسم:** محمد شهيد الاعاجيبي (Mohammed Shaheed Al-Aajeebi)
- **GitHub:** [@moshraheem-sudo](https://github.com/moshraheem-sudo)
- **تطبيق سطح المكتب المرافق:** [MTProxy Desk Desktop App](https://github.com/moshraheem-sudo/MTProxy-Desk)
