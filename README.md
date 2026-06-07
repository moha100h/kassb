# Kassb Bot

ربات تلگرام برای جستجو و خروجی اطلاعات کسب‌وکارهای عمومی از OpenStreetMap.

## نصب سریع (یک دستور)

```bash
mkdir -p /opt/bots/kassb && cd /opt/bots/kassb && git clone https://github.com/moha100h/kassb.git . && bash install.sh
```

فقط **Bot Token** و **Admin ID** می‌پرسد. بقیه خودکار.

## نحوه استفاده

فرمت پیام:
```
شهر | دسته‌بندی
```

مثال‌ها:
```
تهران | رستوران
زنجان | نصاب دوربین مداربسته
تبریز | دندانپزشک
```

## دستورات مفید

```bash
# لاگ
docker logs -f kassb_bot

# ریستارت
docker restart kassb_bot

# آپدیت
cd /opt/bots/kassb && git pull && docker compose up -d --build

# استوپ
docker compose -f /opt/bots/kassb/docker-compose.yml down
```
