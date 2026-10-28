#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Iran SW Radio - Automated Database Update Pipeline
Executes the end-to-end data ingestion, validation, and multi-format export workflow.
Usage:
    python tools/update_database.py [--fetch-online] [--generate-pdf]
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime

# Configure Windows console utf-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, 'tools')

def run_step(step_name, script_path, args=None):
    print(f"\n==================================================")
    print(f"▶ اجرای مرحله: {step_name}")
    print(f"==================================================")
    cmd = [sys.executable, script_path] + (args or [])
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, env=env)
    if res.returncode == 0:
        print(res.stdout)
        print(f"✓ مرحله {step_name} با موفقیت به پایان رسید.")
        return True
    else:
        print(f"❌ خطا در اجرای مرحله {step_name}:")
        print(res.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="ابزار به‌روزرسانی پایگاه داده رادیوهای موج کوتاه ایران")
    parser.add_argument("--fetch-online", action="store_true", help="دریافت آخرین فایل‌های خام از HFCC و EiBi از طریق اینترنت")
    parser.add_argument("--generate-pdf", action="store_true", default=True, help="تولید خودکار فایل PDF قابل چاپ با مرورگر Headless")
    args = parser.parse_args()

    start_time = datetime.now()
    print(f"شروع فرایند به‌روزرسانی در {start_time.strftime('%Y-%m-%d %H:%M:%S')}...")

    # Step 1: Optional download from web
    if args.fetch_online:
        fetch_script = os.path.join(TOOLS_DIR, 'download_raw_sources.py')
        if not run_step("دریافت داده‌های برخط (EiBi و HFCC)", fetch_script):
            print("هشدار: دریافت برخط با خطا مواجه شد؛ ادامه کار با فایل‌های محلی موجود.")

    # Step 2: Build Database (JSON, CSVs, XLSX, TXT)
    db_script = os.path.join(TOOLS_DIR, 'build_database.py')
    if not run_step("تولید و اعتبارسنجی پایگاه داده مرجع و خروجی‌های ساختاریافته", db_script):
        print("توقف به دلیل خطا در ساخت پایگاه داده.")
        sys.exit(1)

    # Step 3: Build Standalone Offline HTML
    html_script = os.path.join(TOOLS_DIR, 'build_html.py')
    if not run_step("کامپایل و بسته‌بندی فایل مستقل HTML آفلاین", html_script):
        print("توقف به دلیل خطا در ساخت HTML.")
        sys.exit(1)

    # Step 4: Generate Printable PDF
    if args.generate_pdf:
        pdf_script = os.path.join(TOOLS_DIR, 'generate_pdf.py')
        run_step("تولید کتابچه راهنمای چاپی PDF با موتور کرومیوم", pdf_script)

    # Step 5: Run Automated Tests
    tests_cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
    print(f"\n==================================================")
    print(f"▶ اجرای آزمون‌های اعتبارسنجی خودکار")
    print(f"==================================================")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    test_res = subprocess.run(tests_cmd, cwd=BASE_DIR, capture_output=True, text=True, env=env)
    print(test_res.stdout)
    if test_res.returncode == 0:
        print("✓ تمام آزمون‌های خودکار با موفقیت پاس شدند.")
    else:
        print("❌ برخی از آزمون‌ها با خطا مواجه شدند:")
        print(test_res.stderr)

    duration = (datetime.now() - start_time).total_seconds()
    print(f"\n==================================================")
    print(f"🎉 به‌روزرسانی و تولید تمام خروجی‌ها در {duration:.2f} ثانیه با موفقیت تکمیل شد.")
    print(f"فایل‌های نهایی در پوشه‌های data/، exports/ و app/ در دسترس هستند.")
    print(f"==================================================")

if __name__ == "__main__":
    main()
