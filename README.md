# Kassb Bot

ربات تلگرام برای جستجو و خروجی اطلاعات کسب‌وکارهای عمومی از OpenStreetMap.

## نصب سریع

```bash
curl -sL https://raw.githubusercontent.com/moha100h/kassb/main/install.sh | bash
```

فقط **Bot Token** و **Admin ID** می‌پرسد.

## نحوه استفاده

فرمت پیام:
```
شهر | دسته‌بندی
```

مثال‌ها:
```
تهران | رستوران
تبریز | دندانپزشک
مشهد | تعمیرگاه خودرو
```

## دستورات مفید

```bash
# لاگ
docker-compose -f /opt/kassb/kassb/docker-compose.yml logs -f

# ریستارت
docker-compose -f /opt/kassb/kassb/docker-compose.yml restart

# استوپ
docker-compose -f /opt/kassb/kassb/docker-compose.yml down
```
