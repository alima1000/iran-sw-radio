# راهنمای ابزارهای داده و به‌روزرسانی (Tools Guide)

این پوشه شامل اسکریپت‌های پایتون برای گردآوری داده‌های فصلی، اعتبارسنجی فرکانس‌ها، تبدیل ساعت‌ها به وقت رسمی تهران و تولید خروجی‌های چندگانه پروژه **Iran SW Radio** است.

---

## ۱. ساختار اسکریپت‌ها

<table dir="rtl" style="width:100%; border-collapse:collapse; text-align:right; direction:rtl;">
  <thead>
    <tr style="background:#1f497d; color:#fff;">
      <th style="padding:8px; border:1px solid #ccc;">نام اسکریپت</th>
      <th style="padding:8px; border:1px solid #ccc;">نقش و وظیفه</th>
      <th style="padding:8px; border:1px solid #ccc;">خروجی‌ها</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding:8px; border:1px solid #ccc;"><code>update_database.py</code></td>
      <td style="padding:8px; border:1px solid #ccc;">پایپ‌لاین اصلی و هماهنگ‌کننده به‌روزرسانی جامع پروژه</td>
      <td style="padding:8px; border:1px solid #ccc;">اجرای تمام مراحل و آزمون‌های خودکار</td>
    </tr>
    <tr>
      <td style="padding:8px; border:1px solid #ccc;"><code>download_raw_sources.py</code></td>
      <td style="padding:8px; border:1px solid #ccc;">دریافت فایل‌های خام فصلی از کنفرانس بین‌المللی HFCC و دایرکتوری EiBi</td>
      <td style="padding:8px; border:1px solid #ccc;">ذخیره در <code>raw_sources/</code></td>
    </tr>
    <tr>
      <td style="padding:8px; border:1px solid #ccc;"><code>build_database.py</code></td>
      <td style="padding:8px; border:1px solid #ccc;">پردازش، فیلتر، راستی‌آزمایی، تبدیل ساعت تهران و تولید پایگاه داده</td>
      <td style="padding:8px; border:1px solid #ccc;">JSON، CSVها، TXTها و فایل اکسل چندبرگه</td>
    </tr>
    <tr>
      <td style="padding:8px; border:1px solid #ccc;"><code>build_html.py</code></td>
      <td style="padding:8px; border:1px solid #ccc;">کامپایل نرم‌افزار تک‌فایلی و آفلاین HTML با تعبیه ۱۰۰٪ داده‌ها و آیکون‌ها</td>
      <td style="padding:8px; border:1px solid #ccc;"><code>app/Iran-SW-Radio-Guide.html</code></td>
    </tr>
    <tr>
      <td style="padding:8px; border:1px solid #ccc;"><code>generate_pdf.py</code></td>
      <td style="padding:8px; border:1px solid #ccc;">تولید کتابچه راهنمای چاپی PDF با موتور رندر کرومیوم بدون دستکاری فونت</td>
      <td style="padding:8px; border:1px solid #ccc;"><code>exports/Iran-SW-Radio-Guide.pdf</code></td>
    </tr>
  </tbody>
</table>

---

## ۲. نحوه اجرای به‌روزرسانی

### الف) بازتولید فوری تمام خروجی‌ها از داده‌های موجود:
در صورتی که داده‌های فایلی تغییر کرده باشند، با اجرای دستور زیر تمام خروجی‌ها (HTML، PDF، اکسل، CSV و TXT) در کمتر از ۲ ثانیه بازسازی می‌شوند:

```bash
python tools/update_database.py
```

### ب) دریافت فایل‌های جدید فصلی از اینترنت:
هنگامی که اینترنت متصل است و جدول فصلی جدید (مثلاً A27 یا B27) از سوی HFCC منتشر شده است:

```bash
python tools/update_database.py --fetch-online
```

---

## ۳. محاسبات زمانی و منطقه زمانی تهران

تمام تبدیل‌های ساعت در تابع `utc_to_tehran_time` و `process_time_span` انجام می‌گیرد:
- **مبنای زمانی:** `UTC+03:30` دقیق و ثابت.
- **تغییر ساعت تابستانی:** ایران از سال ۲۰۲۲ (۱۴۰۱ خورشیدی) قانون تغییر ساعت فصلی را لغو کرده و ساعت کشور در تمام طول سال ۳ ساعت و ۳۰ دقیقه جلوتر از زمان هماهنگ جهانی (UTC) است.
- **عبور از نیمه‌شب:** اگر برنامه از ساعت ۰۰:۰۰ بامداد به وقت تهران عبور کند، برچسب `(روز بعد)` یا `(۲۴ ساعته)` به طور خودکار به داده افزوده می‌شود.
