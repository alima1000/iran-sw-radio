#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates the printable PDF document:
  exports/Iran-SW-Radio-Guide.pdf
Uses headless Chrome / Edge to render a high-fidelity, RTL Persian print template.
"""

import os
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
EXPORTS_DIR = os.path.join(BASE_DIR, 'exports')
os.makedirs(EXPORTS_DIR, exist_ok=True)

def build_pdf():
    json_path = os.path.join(DATA_DIR, 'radio-database.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
        
    schedules = db['schedules']
    stations = {s['station_id']: s for s in db['stations']}
    sources = db['sources']
    meta = db['metadata']

    # Sort schedules:
    # 1. Persian broadcasts sorted by Tehran time
    farsi_scheds = sorted([s for s in schedules if s['language'] in ['fa', 'dr', 'tj']], key=lambda x: (x['time_start_tehran'], x['frequency_khz']))
    # 2. International non-persian schedules
    intl_scheds = sorted([s for s in schedules if s['language'] not in ['fa', 'dr', 'tj']], key=lambda x: (x['time_start_tehran'], x['frequency_khz']))
    # 3. All sorted by frequency
    by_freq = sorted(schedules, key=lambda x: (x['frequency_khz'], x['time_start_tehran']))

    html_doc = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>Iran SW Radio — راهنمای جامع و چاپی رادیوهای موج کوتاه</title>
  <style>
    @page {{
      size: A4 portrait;
      margin: 15mm 12mm 15mm 12mm;
      @bottom-right {{
        content: "Iran SW Radio • نسخه {meta['version']}";
        font-family: 'Vazirmatn', Tahoma, sans-serif;
        font-size: 8pt;
        color: #666;
      }}
      @bottom-left {{
        content: "صفحه " counter(page);
        font-family: 'Vazirmatn', Tahoma, sans-serif;
        font-size: 8pt;
        color: #666;
      }}
    }}

    body {{
      font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Tahoma, sans-serif;
      direction: rtl;
      text-align: right;
      color: #111;
      background: #fff;
      font-size: 9.5pt;
      line-height: 1.6;
    }}

    .cover-header {{
      border-bottom: 2.5px solid #1f497d;
      padding-bottom: 12px;
      margin-bottom: 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .cover-title {{
      font-size: 20pt;
      font-weight: 800;
      color: #1f497d;
      margin-bottom: 4px;
    }}

    .cover-subtitle {{
      font-size: 11pt;
      color: #444;
      font-weight: 600;
    }}

    .meta-box {{
      background: #f0f4f8;
      border: 1px solid #d0dbe5;
      border-radius: 6px;
      padding: 10px 14px;
      margin-bottom: 18px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      font-size: 8.5pt;
    }}

    .meta-item strong {{
      color: #1f497d;
      display: block;
      margin-bottom: 2px;
    }}

    h2.section-title {{
      font-size: 13pt;
      font-weight: 800;
      color: #1f497d;
      background: #eef3f8;
      border-right: 4px solid #1f497d;
      padding: 6px 12px;
      margin-top: 22px;
      margin-bottom: 12px;
      page-break-after: avoid;
    }}

    table.pdf-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 16px;
      font-size: 8.5pt;
      page-break-inside: auto;
    }}

    table.pdf-table tr {{
      page-break-inside: avoid;
      page-break-after: auto;
    }}

    table.pdf-table thead {{
      display: table-header-group;
    }}

    table.pdf-table th {{
      background-color: #1f497d;
      color: #ffffff;
      padding: 6px 8px;
      border: 1px solid #16365c;
      font-weight: 700;
      text-align: right;
      white-space: nowrap;
    }}

    table.pdf-table td {{
      padding: 5px 8px;
      border: 1px solid #ccc;
      vertical-align: middle;
    }}

    table.pdf-table tr:nth-child(even) td {{
      background-color: #f9fbfd;
    }}

    .badge-a {{ background: #e6f4ea; color: #137333; font-weight: 700; padding: 2px 5px; border-radius: 3px; border: 1px solid #ceead6; font-size: 8pt; }}
    .badge-b {{ background: #e8f0fe; color: #1a73e8; font-weight: 700; padding: 2px 5px; border-radius: 3px; border: 1px solid #d2e3fc; font-size: 8pt; }}
    .badge-c {{ background: #fef7e0; color: #b06000; font-weight: 700; padding: 2px 5px; border-radius: 3px; border: 1px solid #fce8b2; font-size: 8pt; }}

    .box-info {{
      background: #fafafa;
      border: 1px solid #e0e0e0;
      border-radius: 6px;
      padding: 12px 14px;
      margin-bottom: 16px;
      font-size: 9pt;
      line-height: 1.8;
      page-break-inside: avoid;
    }}

    .page-break {{
      page-break-before: always;
    }}
  </style>
</head>
<body>

  <!-- COVER HEADER -->
  <div class="cover-header">
    <div>
      <div class="cover-title">Iran SW Radio</div>
      <div class="cover-subtitle">راهنمای جامع، دقیق و آفلاین رادیوهای موج کوتاه (SW) به وقت تهران</div>
    </div>
    <div style="text-align: left; font-size: 8.5pt; color: #555;">
      <div><strong>نسخه سند:</strong> {meta['version']}</div>
      <div><strong>اعتبار جدول:</strong> فصل زمستان B26 (۲۰۲۶-۲۰۲۷)</div>
      <div><strong>ساعت مبنا:</strong> وقت رسمی تهران (UTC+03:30)</div>
    </div>
  </div>

  <div class="meta-box">
    <div class="meta-item">
      <strong>وضعیت کاربرد:</strong>
      طراحی‌شده برای زمان قطع کامل اینترنت بین‌الملل و شرایط اضطراری
    </div>
    <div class="meta-item">
      <strong>آمار پایگاه داده:</strong>
      {meta['stats']['total_stations']} شبکه رادیویی • {meta['stats']['total_schedules']} رکورد پخش • {meta['stats']['total_farsi_schedules']} برنامه فارسی
    </div>
    <div class="meta-item">
      <strong>منابع استناد:</strong>
      اتحادیه بین‌المللی HFCC B26، دایرکتوری EiBi و وب‌سایت‌های رسمی شبکه‌ها
    </div>
  </div>

  <!-- SECTION 1: PERSIAN SCHEDULE -->
  <h2 class="section-title">۱. جدول برنامه‌های فارسی‌زبان به ترتیب ساعت تهران</h2>
  <table class="pdf-table">
    <thead>
      <tr>
        <th style="width: 18%;">ساعت پخش (تهران)</th>
        <th style="width: 14%;">فرکانس (kHz)</th>
        <th style="width: 13%;">باند امواج</th>
        <th style="width: 20%;">نام شبکه</th>
        <th style="width: 25%;">برنامه و فرستنده</th>
        <th style="width: 10%;">اعتبار</th>
      </tr>
    </thead>
    <tbody>
      {''.join([f'''
      <tr>
        <td><strong>{s['time_display_tehran']}</strong></td>
        <td><strong style="color:#1f497d; font-size:9.5pt;">{s['frequency_khz']} kHz</strong></td>
        <td>{s['band_name_fa']}</td>
        <td><strong>{s['station_name_fa']}</strong></td>
        <td>{s['program_title']}<br><small style="color:#555;">فرستنده: {s['transmitter_site']} ({s['transmitter_power_kw'] or '?'} kW)</small></td>
        <td><span class="badge-{'a' if s['confidence_level']=='A' else 'b' if s['confidence_level']=='B' else 'c'}">سطح {s['confidence_level']}</span></td>
      </tr>
      ''' for s in farsi_scheds])}
    </tbody>
  </table>

  <!-- SECTION 2: FREQUENCY ORDERED SPECTRUM -->
  <div class="page-break"></div>
  <h2 class="section-title">۲. مرور جدول به ترتیب صعودی فرکانس (کیلوهرتز kHz)</h2>
  <table class="pdf-table">
    <thead>
      <tr>
        <th style="width: 14%;">فرکانس (kHz)</th>
        <th style="width: 14%;">باند امواج</th>
        <th style="width: 20%;">شبکه و برنامه</th>
        <th style="width: 10%;">زبان</th>
        <th style="width: 18%;">ساعت پخش (تهران)</th>
        <th style="width: 14%;">فرستنده / توان</th>
        <th style="width: 10%;">سطح اطمینان</th>
      </tr>
    </thead>
    <tbody>
      {''.join([f'''
      <tr>
        <td><strong style="color:#1f497d; font-size:10pt;">{s['frequency_khz']}</strong> <small>kHz</small></td>
        <td>{s['band_name_fa']}</td>
        <td><strong>{s['station_name_fa']}</strong><br><small style="color:#555;">{s['program_title']}</small></td>
        <td>{s['language_fa']}</td>
        <td><strong>{s['time_display_tehran']}</strong></td>
        <td>{s['transmitter_site']}<br><small style="color:#666;">{s['transmitter_power_kw'] or '?'} kW</small></td>
        <td><span class="badge-{'a' if s['confidence_level']=='A' else 'b' if s['confidence_level']=='B' else 'c'}">سطح {s['confidence_level']}</span></td>
      </tr>
      ''' for s in by_freq])}
    </tbody>
  </table>

  <!-- SECTION 3: INTERNATIONAL SERVICES -->
  <div class="page-break"></div>
  <h2 class="section-title">۳. ایستگاه‌های مهم بین‌المللی به زبان‌های انگلیسی و عربی در ایران</h2>
  <table class="pdf-table">
    <thead>
      <tr>
        <th style="width: 18%;">ساعت پخش (تهران)</th>
        <th style="width: 14%;">فرکانس (kHz)</th>
        <th style="width: 14%;">باند امواج</th>
        <th style="width: 22%;">شبکه و کشور</th>
        <th style="width: 12%;">زبان</th>
        <th style="width: 20%;">توضیحات و فرستنده</th>
      </tr>
    </thead>
    <tbody>
      {''.join([f'''
      <tr>
        <td><strong>{s['time_display_tehran']}</strong></td>
        <td><strong style="color:#1f497d;">{s['frequency_khz']} kHz</strong></td>
        <td>{s['band_name_fa']}</td>
        <td><strong>{s['station_name_fa']}</strong><br><small style="color:#555;">{s['country_fa']}</small></td>
        <td>{s['language_fa']}</td>
        <td>{s['transmitter_site']} ({s['transmitter_power_kw'] or '?'} kW)</td>
      </tr>
      ''' for s in intl_scheds])}
    </tbody>
  </table>

  <!-- SECTION 4: RECEIVER GUIDE & PROPAGATION -->
  <h2 class="section-title">۴. راهنمای کاربردی استفاده از گیرنده رادیو و رفع پارازیت</h2>
  <div class="box-info">
    <p><strong>۱. تنظیم گیرنده:</strong> رادیو را روی حالت <strong>AM</strong> قرار دهید. برای تمام ایستگاه‌های این راهنما حالت AM استاندارد کافی است.</p>
    <p><strong>۲. قاعده انتشار روز و شب:</strong> در طول شب، فرکانس‌های زیر ۱۰ مگاهرتز (باند ۴۹ متر مثل ۵۸۶۰ و ۵۸۹۰ و باند ۴۱ متر مثل ۷۴۱۵ کیلوهرتز) بیشترین قدرت را دارند. در طول روز، فرکانس‌های بالای ۱۲ مگاهرتز (باند ۲۵ متر مثل ۱۲۰۰۵ و باند ۱۹ متر مثل ۱۵۷۲۰ و ۱۵۱۳۰ کیلوهرتز) دریافت بسیار شفافی دارند.</p>
    <p><strong>۳. رفع نویز خانگی:</strong> شارژر موبایل، لامپ کم‌مصرف، مودم و تلویزیون تولیدکننده نویز هستند. رادیو را با باتری و در فاصله ۳ متری از پریزها و وسایل برقی استفاده کنید.</p>
    <p><strong>۴. آنتن سیمی دست‌ساز (تقویت فوری):</strong> یک رشته سیم نازک ۳ تا ۵ متری را به نوک آنتن تلسکوپی رادیو متصل کنید و انتهای آن را بیرون از پنجره یا روی دیوار آویزان نمایید.</p>
  </div>

  <!-- SECTION 5: DATA SOURCES & CONFIDENCE -->
  <h2 class="section-title">۵. مستندات، منابع رسمی و سطوح اطمینان داده‌ها</h2>
  <div class="box-info">
    <p><strong>سطح A (تأییدشده رسمی):</strong> تطابق کامل بین سند هماهنگی بین‌المللی HFCC B26 اتحادیه مخابرات و وبگاه رسمی سازمان فرستنده (رادیو فردا، رادیو چین، صدای ترکیه، رادیو هند، رادیو ژاپن، رادیو کویت، پارس‌تودی صداوسیما، بی‌بی‌سی انگلیسی، VOA و رادیو رومانی).</p>
    <p><strong>سطح B (تأیید متقاطع تخصصی):</strong> رصد مستقل در دایرکتوری تخصصی EiBi و لاگ‌های مانیتورینگ شنوندگان (ایران اینترنشنال اسپیس‌لاین، رادیو زمانه، رادیو مژده).</p>
    <p><strong>سطح C (پخش اضطراری یا نیازمند بررسی):</strong> فرکانس‌های رزرو بحران بی‌بی‌سی فارسی یا ایستگاه‌های احزاب سیاسی که در بازه‌های زمانی کوتاه پخش می‌شوند.</p>
    <p><strong>شبکه‌های تاریخی و غیرفعال:</strong> رادیو دویچه وله فارسی (تعطیل شده در سال ۲۰۱۱) و رادیو فرانسه فارسی (RFI) دیگر هیچ پخش رادیویی روی موج کوتاه ندارند.</p>
  </div>

  <div style="text-align: center; font-size: 8pt; color: #888; margin-top: 15px; border-top: 1px solid #ddd; padding-top: 8px;">
    تهیه‌شده توسط پروژه Iran SW Radio • نسخه 2.0.0-B26 • تاریخ تولید: ۲۸ اکتبر ۲۰۲۶ (۷ آبان ۱۴۰۵)
  </div>

</body>
</html>
"""

    html_file = os.path.join(EXPORTS_DIR, 'print_template.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_doc)
    print(f"Saved print HTML template: {html_file}")

    # Generate PDF using Chrome / Edge headless
    pdf_out = os.path.join(EXPORTS_DIR, 'Iran-SW-Radio-Guide.pdf')
    browsers = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    ]
    
    selected_browser = None
    for b in browsers:
        if os.path.exists(b):
            selected_browser = b
            break
            
    if not selected_browser:
        print("Error: Neither Chrome nor Edge executable was found for PDF generation.")
        return False
        
    cmd = [
        selected_browser,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_out}",
        "--no-pdf-header-footer",
        html_file
    ]
    print(f"Executing: {' '.join(cmd[:4])} ...")
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if os.path.exists(pdf_out) and os.path.getsize(pdf_out) > 1000:
        print(f"Successfully generated PDF: {pdf_out} ({os.path.getsize(pdf_out)} bytes)")
        return True
    else:
        print("PDF generation failed:", res.stderr)
        return False

if __name__ == "__main__":
    build_pdf()
