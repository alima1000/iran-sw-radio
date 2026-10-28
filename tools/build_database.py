#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Iran SW Radio Database Builder
Generates:
  - data/radio-database.json
  - data/stations.csv
  - data/schedules.csv
  - data/sources.csv
  - exports/Iran-SW-Radio-Emergency-Quick-Reference.txt
  - exports/Iran-SW-Radio-Frequency-Guide.txt
  - exports/Iran-SW-Radio-Database.xlsx (multi-sheet Excel)
"""

import os
import json
import csv
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
EXPORTS_DIR = os.path.join(BASE_DIR, 'exports')
RAW_DIR = os.path.join(BASE_DIR, 'raw_sources')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# TIME CALCULATION: STRICT UTC+03:30 (TEHRAN)
# ---------------------------------------------------------------------------
def utc_to_tehran_time(utc_time_str):
    utc_clean = utc_time_str.replace(':', '').strip()
    if len(utc_clean) == 3:
        utc_clean = '0' + utc_clean
    if len(utc_clean) != 4 or not utc_clean.isdigit():
        return utc_time_str, 0
    h = int(utc_clean[:2])
    m = int(utc_clean[2:])
    tot_mins = h * 60 + m + 210  # 3h 30m = 210 mins
    day_off = tot_mins // 1440
    rem_mins = tot_mins % 1440
    th_h = rem_mins // 60
    th_m = rem_mins % 60
    return f"{th_h:02d}:{th_m:02d}", day_off

def process_time_span(start_utc, end_utc):
    s_th, s_off = utc_to_tehran_time(start_utc)
    e_th, e_off = utc_to_tehran_time(end_utc)
    
    s_h, s_m = int(start_utc[:2]), int(start_utc[2:])
    e_h, e_m = int(end_utc[:2]), int(end_utc[2:])
    start_total = s_h * 60 + s_m
    end_total = e_h * 60 + e_m
    
    if end_total <= start_total:
        duration = (end_total + 1440) - start_total
    else:
        duration = end_total - start_total
        
    crosses_midnight = False
    if duration == 1440:
        desc = f"{s_th} تا {e_th} (۲۴ ساعته)"
    elif e_off > s_off or (end_total < start_total):
        desc = f"{s_th} تا {e_th} (روز بعد)"
        crosses_midnight = True
    else:
        desc = f"{s_th} تا {e_th}"
        
    return {
        'start_tehran': s_th,
        'end_tehran': e_th,
        'display_tehran': desc,
        'crosses_midnight': crosses_midnight,
        'duration_minutes': duration
    }

def classify_band(freq_khz):
    f = float(freq_khz)
    if 520 <= f <= 1710:
        return {'code': 'MW', 'name_fa': 'موج متوسط (MW)', 'name_en': 'Medium Wave', 'prop_fa': 'پوشش شبانگاهی پایدار منطقه‌ای'}
    elif 2300 <= f <= 2500:
        return {'code': '120m', 'name_fa': 'باند ۱۲۰ متر', 'name_en': '120m Band', 'prop_fa': 'مخصوص شب؛ تضعیف شدید در روز'}
    elif 3200 <= f <= 3450:
        return {'code': '90m', 'name_fa': 'باند ۹۰ متر', 'name_en': '90m Band', 'prop_fa': 'باند شبانگاهی؛ دریافت فواصل نزدیک و منطقه‌ای'}
    elif 3900 <= f <= 4050:
        return {'code': '75m', 'name_fa': 'باند ۷۵ متر', 'name_en': '75m Band', 'prop_fa': 'شبانگاهی در فصول سرد سال'}
    elif 4750 <= f <= 5100:
        return {'code': '60m', 'name_fa': 'باند ۶۰ متر', 'name_en': '60m Band', 'prop_fa': 'پایان بعدازظهر تا سحرگاه'}
    elif 5800 <= f <= 6300:
        return {'code': '49m', 'name_fa': 'باند ۴۹ متر', 'name_en': '49m Band', 'prop_fa': 'قدرتمندترین باند شبانگاهی موج کوتاه در ایران؛ عبور عالی از موانع'}
    elif 7200 <= f <= 7600:
        return {'code': '41m', 'name_fa': 'باند ۴۱ متر', 'name_en': '41m Band', 'prop_fa': 'باند بسیار کلیدی در ساعات غروب، شب و اوایل صبح'}
    elif 9300 <= f <= 10000:
        return {'code': '31m', 'name_fa': 'باند ۳۱ متر', 'name_en': '31m Band', 'prop_fa': 'محبوب‌ترین و پایدارترین باند شبانه‌روزی برای ارتباطات بین‌المللی'}
    elif 11500 <= f <= 12200:
        return {'code': '25m', 'name_fa': 'باند ۲۵ متر', 'name_en': '25m Band', 'prop_fa': 'دریافت خوب در ساعات بعدازظهر و غروب'}
    elif 13500 <= f <= 13900:
        return {'code': '22m', 'name_fa': 'باند ۲۲ متر', 'name_en': '22m Band', 'prop_fa': 'باند ویژه روزانه برای مسافت‌های بسیار دور'}
    elif 15000 <= f <= 15900:
        return {'code': '19m', 'name_fa': 'باند ۱۹ متر', 'name_en': '19m Band', 'prop_fa': 'بهترین باند روزانه در تمام فصول سال؛ سیگنال شفاف از آسیا و اروپا'}
    elif 17400 <= f <= 18100:
        return {'code': '16m', 'name_fa': 'باند ۱۶ متر', 'name_en': '16m Band', 'prop_fa': 'روزانه در ساعات اوج تابش خورشید'}
    elif 21400 <= f <= 21850:
        return {'code': '13m', 'name_fa': 'باند ۱۳ متر', 'name_en': '13m Band', 'prop_fa': 'روزانه در شرایط انتشار عالی خورشیدی'}
    else:
        return {'code': 'OTHER', 'name_fa': 'باند فرعی SW', 'name_en': 'SW Out of Band', 'prop_fa': 'باند فرعی یا ارتباطات اختصاصی'}

# ---------------------------------------------------------------------------
# SOURCES DICTIONARY
# ---------------------------------------------------------------------------
SOURCES_DATA = [
    {
        "source_id": "SRC-HFCC-B26",
        "name_fa": "کنفرانس بین‌المللی هماهنگی فرکانس‌های بالا (HFCC - فصل زمستان B26)",
        "name_en": "HFCC High Frequency Coordination Conference - Winter Season B26",
        "type": "official_treaty",
        "type_fa": "مرجع رسمی هماهنگی بین‌المللی اتحادیه مخابرات (ITU)",
        "url": "http://www.hfcc.org/data/b26/",
        "collected_date": "2026-10-27",
        "valid_period": "2026-10-25 تا 2027-03-27",
        "description_fa": "جدول رسمی ثبت‌شده توسط اپراتورهای فرستنده و دولت‌ها در سازمان HFCC برای فصل زمستان ۲۰۲۶-۲۰۲۷"
    },
    {
        "source_id": "SRC-HFCC-A26",
        "name_fa": "کنفرانس بین‌المللی هماهنگی فرکانس‌های بالا (HFCC - فصل تابستان A26)",
        "name_en": "HFCC High Frequency Coordination Conference - Summer Season A26",
        "type": "official_treaty",
        "type_fa": "مرجع رسمی هماهنگی بین‌المللی اتحادیه مخابرات (ITU)",
        "url": "http://www.hfcc.org/data/a26/",
        "collected_date": "2026-10-25",
        "valid_period": "2026-03-29 تا 2026-10-25",
        "description_fa": "پایگاه داده بین‌المللی اتحادیه جهانی مخابرات و سازمان هماهنگی موج کوتاه برای فصل تابستان ۲۰۲۶"
    },
    {
        "source_id": "SRC-EIBI-A26",
        "name_fa": "پایگاه داده فرکانس‌های رادیویی EiBi (نسخه اکتبر ۲۰۲۶)",
        "name_en": "EiBi Shortwave Schedules by Eike Bierwirth",
        "type": "specialized_aggregator",
        "type_fa": "پایگاه تخصصی پایش امواج کوتاه رادیویی",
        "url": "http://www.eibispace.de/",
        "collected_date": "2026-10-19",
        "valid_period": "2026-03-29 تا 2026-10-25 (به‌روزرسانی ۱۹ اکتبر ۲۰۲۶)",
        "description_fa": "معتبرترین و پرکاربردترین دایرکتوری مانیتورینگ شنوندگان رادیویی و لاگ‌های میدانی در سراسر جهان"
    },
    {
        "source_id": "SRC-RADIOFARDA-OFFICIAL",
        "name_fa": "جدول فرکانس‌های رسمی رادیو فردا (RFE/RL)",
        "name_en": "Radio Farda Official Transmission Schedule",
        "type": "broadcaster_official",
        "type_fa": "وب‌سایت رسمی شبکه رادیویی",
        "url": "https://www.radiofarda.com/",
        "collected_date": "2026-10-28",
        "valid_period": "جاری ۲۰۲۶-۲۰۲۷",
        "description_fa": "فرکانس‌های پخش زنده رادیویی رادیو فردا روی موج کوتاه و متوسط با فرستنده‌های کویت، آلمان و ارمنستان"
    },
    {
        "source_id": "SRC-CRI-OFFICIAL",
        "name_fa": "سرویس فارسی رادیو بین‌المللی چین (CRI / صدای چین)",
        "name_en": "China Radio International Persian Service",
        "type": "broadcaster_official",
        "type_fa": "وب‌سایت رسمی شبکه رادیویی",
        "url": "http://persian.cri.cn/",
        "collected_date": "2026-10-28",
        "valid_period": "جاری ۲۰۲۶-۲۰۲۷",
        "description_fa": "جدول پخش برنامه‌های موج کوتاه بخش فارسی رادیو پکن با فرستنده‌های ۵۰۰ کیلوواتی شی‌آن و کاشغر"
    },
    {
        "source_id": "SRC-TRT-OFFICIAL",
        "name_fa": "بخش فارسی صدای ترکیه (TRT Voice of Turkey)",
        "name_en": "Voice of Turkey Persian Service Official Schedule",
        "type": "broadcaster_official",
        "type_fa": "وب‌سایت رسمی شبکه دولتی ترکیه",
        "url": "https://www.trtfarsi.com/",
        "collected_date": "2026-10-28",
        "valid_period": "جاری ۲۰۲۶-۲۰۲۷",
        "description_fa": "ساعات و فرکانس‌های پخش امواج کوتاه از ایستگاه امیرلر ترکیه به سمت خاورمیانه و فلات ایران"
    },
    {
        "source_id": "SRC-AIR-OFFICIAL",
        "name_fa": "بخش خدمات برون‌مرزی رادیو هند (Akashvani / AIR External Services)",
        "name_en": "All India Radio External Services Division",
        "type": "broadcaster_official",
        "type_fa": "وب‌سایت رسمی رادیو دولتی هند",
        "url": "https://akashvani.gov.in/",
        "collected_date": "2026-10-28",
        "valid_period": "فصل B26 / جاری",
        "description_fa": "جدول پخش رسمی برنامه‌های فارسی رادیو دهلی نو/بنگالورو برای شنوندگان ایران و افغانستان"
    },
    {
        "source_id": "SRC-NHK-OFFICIAL",
        "name_fa": "رادیو بین‌المللی ژاپن (NHK World-Japan بخش فارسی)",
        "name_en": "NHK World-Japan Persian Radio Broadcasts",
        "type": "broadcaster_official",
        "type_fa": "وب‌سایت رسمی رادیو و تلویزیون ملی ژاپن",
        "url": "https://www3.nhk.or.jp/nhkworld/fa/",
        "collected_date": "2026-10-28",
        "valid_period": "فصل جاری ۲۰۲۶",
        "description_fa": "پخش برنامه رادیویی به زبان فارسی از فرستنده یاماتا ژاپن و تقویت‌کننده‌های منطقه‌ای"
    },
    {
        "source_id": "SRC-KUWAIT-OFFICIAL",
        "name_fa": "بخش برون‌مرزی رادیو کویت (Ministry of Information Kuwait)",
        "name_en": "Radio Kuwait Persian External Service",
        "type": "broadcaster_official",
        "type_fa": "وب‌سایت رسمی وزارت اطلاع‌رسانی کویت",
        "url": "https://media.gov.kw/",
        "collected_date": "2026-10-28",
        "valid_period": "جاری ۲۰۲۶",
        "description_fa": "پخش برنامه روزانه زبان فارسی از ایستگاه پرقدرت الکبد به سوی جنوب و مرکز ایران"
    },
    {
        "source_id": "SRC-SHORTWAVE-INFO",
        "name_fa": "دایرکتوری مانیتورینگ Short-Wave.info و Shortwave DB",
        "name_en": "Short-Wave.info & ShortwaveDB Live Monitoring",
        "type": "monitoring_aggregator",
        "type_fa": "سامانه پایش سیگنال و لاگ‌های جهانی",
        "url": "https://short-wave.info/",
        "collected_date": "2026-10-28",
        "valid_period": "پایش برخط ۲۰۲۶",
        "description_fa": "گزارش‌های مانیتورینگ رسیورهای راه دور (WebSDR و KiwiSDR) شنوندگان در خاورمیانه و اروپا"
    }
]

# ---------------------------------------------------------------------------
# STATIONS DATABASE
# ---------------------------------------------------------------------------
STATIONS_DATA = [
    {
        "station_id": "STN-FARDA",
        "name_fa": "رادیو فردا",
        "name_en": "Radio Farda (RFE/RL)",
        "country": "USA",
        "country_fa": "ایالات متحده / چک (پراگ)",
        "broadcaster": "RFE/RL / USAGM",
        "languages": ["fa"],
        "languages_fa": ["فارسی"],
        "category": "news",
        "category_fa": "خبری و تحلیلی",
        "sw_status": "active",
        "sw_status_fa": "فعال مستمر روی موج کوتاه و متوسط",
        "website": "https://www.radiofarda.com",
        "description_fa": "بخش فارسی رادیو اروپای آزاد / رادیو آزادی با پخش شبانه‌روزی اخبار، گزارش، موسیقی و برنامه‌های فرهنگی. دارای قوی‌ترین آرایه فرستنده‌های رله در کویت و اروپا.",
        "primary_transmitters_fa": "الکبد (کویت)، بیبلیس (آلمان)، ووفِرتون (بریتانیا)، گاوار (ارمنستان)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت در جدول رسمی HFCC B26، پایگاه EiBi و پخش مستقیم روزانه"
    },
    {
        "station_id": "STN-CRI",
        "name_fa": "رادیو بین‌المللی چین (بخش فارسی)",
        "name_en": "China Radio International (CRI Persian)",
        "country": "CHN",
        "country_fa": "چین",
        "broadcaster": "China Media Group (CMG)",
        "languages": ["fa"],
        "languages_fa": ["فارسی"],
        "category": "general",
        "category_fa": "عمومی، خبری و فرهنگی",
        "sw_status": "active",
        "sw_status_fa": "فعال با فرستنده‌های پرقدرت ۵۰۰ کیلووات",
        "website": "http://persian.cri.cn",
        "description_fa": "سرویس فارسی رادیو پکن با پوشش اخبار چین، ایران و جهان، آموزش زبان چینی، فرهنگ و موسیقی شرقی. فرستنده‌های غول‌پیکر شی‌آن و کاشغر از رساترین سیگنال‌های دریافتی در ایران هستند.",
        "primary_transmitters_fa": "شی‌آن (چین)، کاشغر (سین‌کیانگ)، پکن",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی در هماهنگی بین‌المللی HFCC B26 و وب‌سایت رسمی شبکه"
    },
    {
        "station_id": "STN-TRT",
        "name_fa": "صدای ترکیه (TRT بخش فارسی)",
        "name_en": "Voice of Turkey (TRT Persian)",
        "country": "TUR",
        "country_fa": "ترکیه",
        "broadcaster": "Turkish Radio and Television Corporation (TRT)",
        "languages": ["fa"],
        "languages_fa": ["فارسی"],
        "category": "general",
        "category_fa": "عمومی، خبری و منطقه‌ای",
        "sw_status": "active",
        "sw_status_fa": "فعال با پخش فصلی روزانه",
        "website": "https://www.trtfarsi.com",
        "description_fa": "بخش فارسی سازمان رادیو و تلویزیون دولتی ترکیه؛ پخش اخبار ترکیه و منطقه، روابط دو کشور، برنامه‌های ادبی، گردشگری و تحلیل رویدادها از آنکارا.",
        "primary_transmitters_fa": "امیرلر (آنکارا - ۵۰۰ کیلووات)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: تأییدشده در هماهنگی رسمی اتحادیه مخابرات HFCC و دایرکتوری EiBi"
    },
    {
        "station_id": "STN-AIR",
        "name_fa": "رادیو هند (آکاشوانی / بخش فارسی)",
        "name_en": "All India Radio (Akashvani Persian)",
        "country": "IND",
        "country_fa": "هند",
        "broadcaster": "Prasar Bharati / External Services Division",
        "languages": ["fa"],
        "languages_fa": ["فارسی"],
        "category": "culture",
        "category_fa": "فرهنگی، موسیقی و خبری",
        "sw_status": "active",
        "sw_status_fa": "فعال در ساعات صبح و غروب",
        "website": "https://akashvani.gov.in",
        "description_fa": "سرویس کهن فارسی رادیو دهلی با پیشینه چندین دهه پخش رادیویی؛ شامل موسیقی اصیل هندی، ادبیات مشترک پارسی و هند، اخبار شبه‌قاره و روابط بین‌الملل.",
        "primary_transmitters_fa": "بنگالورو (۲۵۰ کیلووات)، دهلی (۱۰۰ کیلووات)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت در جدول HFCC B26، وب‌سایت دولتی پراسار بهاراتی و لاگ‌های مانیتورینگ"
    },
    {
        "station_id": "STN-NHK",
        "name_fa": "رادیو ژاپن (NHK World بخش فارسی)",
        "name_en": "NHK World-Japan (Persian Service)",
        "country": "JPN",
        "country_fa": "ژاپن",
        "broadcaster": "Nippon Hoso Kyokai (NHK)",
        "languages": ["fa"],
        "languages_fa": ["فارسی"],
        "category": "general",
        "category_fa": "عمومی، علمی و فرهنگی",
        "sw_status": "active",
        "sw_status_fa": "فعال روی موج کوتاه و تقویت‌کننده موج متوسط",
        "website": "https://www3.nhk.or.jp/nhkworld/fa/",
        "description_fa": "سرویس برون‌مرزی رادیو و تلویزیون ملی ژاپن؛ ارائه اخبار شرق آسیا، دستاوردهای علمی و صنعتی ژاپن، آموزش زبان ژاپنی و موسیقی سنتی.",
        "primary_transmitters_fa": "یاماتا (ژاپن - ۳۰۰ کیلووات)، دوشنبه (تاجیکستان - موج متوسط)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی در جدول HFCC B26 و وبگاه رسمی ان‌اچ‌کی ژاپن"
    },
    {
        "station_id": "STN-KUWAIT",
        "name_fa": "رادیو کویت (بخش فارسی)",
        "name_en": "Radio Kuwait (Persian External Service)",
        "country": "KWT",
        "country_fa": "کویت",
        "broadcaster": "Ministry of Information, State of Kuwait",
        "languages": ["fa"],
        "languages_fa": ["فارسی"],
        "category": "general",
        "category_fa": "عمومی، مذهبی و منطقه‌ای",
        "sw_status": "active",
        "sw_status_fa": "فعال روزانه در ساعات ظهر",
        "website": "https://media.gov.kw",
        "description_fa": "برنامه فارسی رادیو دولتی کویت؛ اخبار جهان اسلام، خلیج فارس، روابط همسایگان، برنامه‌های قرآنی و تواشیح با فرستنده پرقدرت واقع در مجاورت مرزهای ایران.",
        "primary_transmitters_fa": "الکبد (کویت - ۲۵۰ کیلووات)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی در هماهنگی بین‌المللی B26 و EiBi A26"
    },
    {
        "station_id": "STN-IRAN-INTL",
        "name_fa": "صدا و سیمای ایران اینترنشنال (رله موج کوتاه)",
        "name_en": "Iran International TV (Shortwave Audio Relay)",
        "country": "GBR",
        "country_fa": "بریتانیا (لندن)",
        "broadcaster": "Volant Media / Spaceline Bulgaria",
        "languages": ["fa"],
        "languages_fa": ["فارسی"],
        "category": "news",
        "category_fa": "خبری و اطلاع‌رسانی اضطراری",
        "sw_status": "active",
        "sw_status_fa": "فعال در ساعات شب تا بامداد",
        "website": "https://iranintl.com",
        "description_fa": "پخش صوتی برنامه‌های تلویزیون ۲۴ ساعته ایران اینترنشنال از طریق ایستگاه‌های فرستنده اروپایی اسپیس‌لاین در بلغارستان برای زمان‌های بحرانی و قطعی اینترنت.",
        "primary_transmitters_fa": "کوستینبرود (بلغارستان - ۱۰۰ کیلووات)، گاوار (ارمنستان - MW)",
        "confidence_level": "B",
        "confidence_description_fa": "سطح B: تأییدشده در دایرکتوری تخصصی EiBi و لاگ‌های شنوندگان مستقل"
    },
    {
        "station_id": "STN-ZAMANEH",
        "name_fa": "رادیو زمانه",
        "name_en": "Radio Zamaneh",
        "country": "NLD",
        "country_fa": "هلند (آمستردام)",
        "broadcaster": "Stichting Press Now / Zamaneh Media",
        "languages": ["fa"],
        "languages_fa": ["فارسی"],
        "category": "culture",
        "category_fa": "اجتماعی، فرهنگی و تحلیلی",
        "sw_status": "active",
        "sw_status_fa": "فعال شبانگاهی",
        "website": "https://www.radiozamaneh.com",
        "description_fa": "رادیوی مستقل اجتماعی، مدنی، ادبی و حقوق بشری مستقر در آمستردام هلند با پخش برنامه شبانه از طریق فرستنده‌های رله موج کوتاه در اروپای شرقی.",
        "primary_transmitters_fa": "کوستینبرود (بلغارستان)",
        "confidence_level": "B",
        "confidence_description_fa": "سطح B: ثبت در فهرست فصلی EiBi و گزارش‌های شنوندگان امواج کوتاه"
    },
    {
        "station_id": "STN-BBC-PERSIAN",
        "name_fa": "رادیو فارسی بی‌بی‌سی (پخش اضطراری و رله‌ها)",
        "name_en": "BBC Persian Radio (Emergency Relays)",
        "country": "GBR",
        "country_fa": "بریتانیا (لندن)",
        "broadcaster": "BBC World Service",
        "languages": ["fa"],
        "languages_fa": ["فارسی"],
        "category": "news",
        "category_fa": "خبری و تحلیلی",
        "sw_status": "emergency_only",
        "sw_status_fa": "پخش اضطراری / غیرمستمر پس از تعطیلی بخش عادی",
        "website": "https://www.bbc.com/persian",
        "description_fa": "بخش عادی رادیو فارسی بی‌بی‌سی در فروردین ۱۴۰۲ تعطیل شد، اما سرویس جهانی بی‌بی‌سی فرکانس‌های رزرو روی موج کوتاه و متوسط را برای شرایط بحرانی، جنگ یا قطعی سرتاسری اینترنت فعال نگه می‌دارد.",
        "primary_transmitters_fa": "سیلان (سری‌لانکا)، زیگی (قبرس)، الاشخره (عمان - MW)",
        "confidence_level": "C",
        "confidence_description_fa": "سطح C: ثبت فرکانس‌های رزرو در HFCC B26؛ نیازمند بررسی فعال بودن در روز مورد نظر"
    },
    {
        "station_id": "STN-VOA-PERSIAN",
        "name_fa": "صدای آمریکا (VOA بخش فارسی)",
        "name_en": "Voice of America (VOA Persian)",
        "country": "USA",
        "country_fa": "ایالات متحده (واشنگتن)",
        "broadcaster": "U.S. Agency for Global Media (USAGM)",
        "languages": ["fa"],
        "languages_fa": ["فارسی"],
        "category": "news",
        "category_fa": "خبری و سیاسی",
        "sw_status": "active",
        "sw_status_fa": "فعال مستمر ۲۴ ساعته روی موج متوسط (۱۵۴۸ کیلوهرتز)",
        "website": "https://ir.voanews.com",
        "description_fa": "برنامه‌های فارسی صدای آمریکا؛ علاوه بر پخش رادیویی ۲۴ ساعته از فرستنده قدرتمند کویت در موج متوسط، برنامه‌های آن با رادیو فردا در موج کوتاه هم‌پوشانی دارند.",
        "primary_transmitters_fa": "الکبد (کویت - فرستنده فوق‌العاده قوی ۱۵۴۸ کیلوهرتز)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی در اتحادیه ارتباطات جهانی و تأیید پخش مستمر"
    },
    {
        "station_id": "STN-OPPOSITION-CLANDESTINE",
        "name_fa": "شبکه‌های سیاسی و رادیوهای زیرزمینی (پیام، براندازی، مجاهد)",
        "name_en": "Iranian Opposition & Clandestine SW Radios",
        "country": "CLA",
        "country_fa": "ایستگاه‌های متغیر و برون‌مرزی",
        "broadcaster": "احزاب و گروه‌های مختلف سیاسی مخالف",
        "languages": ["fa"],
        "languages_fa": ["فارسی"],
        "category": "opposition",
        "category_fa": "سیاسی و اپوزیسیون",
        "sw_status": "clandestine",
        "sw_status_fa": "پخش متغیر با فرستنده‌های اجاره‌ای",
        "website": None,
        "description_fa": "ایستگاه‌های مختلف سیاسی شامل رادیو پیام، رادیو مجاهدین، رادیو براندازی و رادیو ملت که در ساعات مشخص عصر و شب از فرستنده‌های کوتاه‌مدت پخش می‌شوند.",
        "primary_transmitters_fa": "فرستنده‌های تجاری اجاره‌ای در اروپای شرقی و سایت‌های متغیر",
        "confidence_level": "C",
        "confidence_description_fa": "سطح C: ثبت در لاگ‌های EiBi و گزارش‌های ثبت‌شده شنوندگان DX"
    },
    {
        "station_id": "STN-RELIGIOUS-TWR-BV",
        "name_fa": "رادیوهای فرهنگی و مذهبی (رادیو مژده / ترانس ورلد و ندای کتاب مقدس)",
        "name_en": "Christian Religious & Cultural Broadcasts (TWR & Bible Voice)",
        "country": "USA",
        "country_fa": "بین‌المللی (آمریکا، کانادا، سوئیس)",
        "broadcaster": "TWR / Bible Voice Broadcasting",
        "languages": ["fa"],
        "languages_fa": ["فارسی"],
        "category": "religious",
        "category_fa": "مذهبی و نیایشی",
        "sw_status": "active",
        "sw_status_fa": "فعال در روزها و ساعات تعیین‌شده",
        "website": "https://www.twr.org",
        "description_fa": "برنامه‌های دینی و فرهنگی مسیحی به زبان فارسی شامل موعظه، سرودهای نیایشی، آرامش روان و پاسخ به پرسش‌های دینی.",
        "primary_transmitters_fa": "گاوار (ارمنستان)، کوستینبرود (بلغارستان)، نائن (آلمان)",
        "confidence_level": "B",
        "confidence_description_fa": "سطح B: تأییدشده در مستندات رسمی TWR و دایرکتوری EiBi"
    },
    {
        "station_id": "STN-IRIB-VOIRI",
        "name_fa": "صدای جمهوری اسلامی ایران (سرویس‌های برون‌مرزی صدا و سیما)",
        "name_en": "Voice of the Islamic Republic of Iran (IRIB External)",
        "country": "IRN",
        "country_fa": "ایران (تهران)",
        "broadcaster": "Islamic Republic of Iran Broadcasting (IRIB)",
        "languages": ["dr", "tj", "ku", "ar", "en", "ps"],
        "languages_fa": ["دری", "تاجیکی", "کردی", "عربی", "انگلیسی", "پشتو"],
        "category": "general",
        "category_fa": "دولتی، عمومی و منطقه‌ای",
        "sw_status": "active",
        "sw_status_fa": "فعال با فرستنده‌های ۵۰۰ کیلووات داخلی",
        "website": "https://parstoday.ir",
        "description_fa": "شبکه برون‌مرزی صدای جمهوری اسلامی ایران (پارس تودی)؛ پخش برنامه‌های مختلف به زبان‌های حوزه فارسی‌زبان (دری افغانستان، تاجیکی، کردی) و زبان‌های بین‌المللی از دکل‌های غول‌پیکر کرج و سیرجان.",
        "primary_transmitters_fa": "کمال‌آباد (کرج)، سیرجان (کرمان)، زاهدان",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی در جدول هماهنگی HFCC B26 و رسانه ملی"
    },
    {
        "station_id": "STN-BBC-WS-EN",
        "name_fa": "سرویس جهانی بی‌بی‌سی (انگلیسی و عربی)",
        "name_en": "BBC World Service (English & Arabic)",
        "country": "GBR",
        "country_fa": "بریتانیا",
        "broadcaster": "BBC World Service",
        "languages": ["en", "ar"],
        "languages_fa": ["انگلیسی", "عربی"],
        "category": "news",
        "category_fa": "بین‌المللی و خبری",
        "sw_status": "active",
        "sw_status_fa": "فعال ۲۴ ساعته با چندین فرکانس همزمان",
        "website": "https://www.bbc.com/worldserviceradio",
        "description_fa": "مشهورترین سرویس خبری موج کوتاه در جهان؛ منبع اصلی اخبار موثق بین‌المللی به زبان انگلیسی در صورت نبود یا اختلال روی سرویس‌های فارسی.",
        "primary_transmitters_fa": "زیگی (قبرس)، عمان، سنگاپور، بریتانیا",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: تأیید قطعی HFCC B26 و جدول رسمی BBC"
    },
    {
        "station_id": "STN-VOA-EN",
        "name_fa": "صدای آمریکا (سرویس بین‌المللی انگلیسی)",
        "name_en": "Voice of America (VOA English)",
        "country": "USA",
        "country_fa": "ایالات متحده",
        "broadcaster": "USAGM",
        "languages": ["en"],
        "languages_fa": ["انگلیسی"],
        "category": "news",
        "category_fa": "بین‌المللی و خبری",
        "sw_status": "active",
        "sw_status_fa": "فعال مستمر در طول روز",
        "website": "https://www.voanews.com",
        "description_fa": "پخش اخبار بین‌المللی و گزارش‌های تحلیلی به زبان انگلیسی روان (Special English) و استاندارد قابل استفاده برای تمام شنوندگان جهانی.",
        "primary_transmitters_fa": "کویت، آلمان، ووفِرتون، جزایر اقیانوس آرام",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی در HFCC B26"
    },
    {
        "station_id": "STN-RRI",
        "name_fa": "رادیو رومانی بین‌المللی (RRI)",
        "name_en": "Radio Romania International",
        "country": "ROU",
        "country_fa": "رومانی",
        "broadcaster": "Societatea Română de Radiodifuziune",
        "languages": ["en", "fr", "ar", "ro"],
        "languages_fa": ["انگلیسی", "فرانسوی", "عربی", "رومانیایی"],
        "category": "general",
        "category_fa": "فرهنگی و بین‌المللی",
        "sw_status": "active",
        "sw_status_fa": "فعال با سیگنال قدرتمند در ایران",
        "website": "https://www.rri.ro",
        "description_fa": "یکی از وفادارترین شبکه‌های موج کوتاه در اروپا با فرستنده‌های بسیار پرقدرت ۳۰۰ کیلوواتی که سیگنال آن در تمام نقاط فلات ایران شفاف شنیده می‌شود.",
        "primary_transmitters_fa": "گالوانی (رومانی)، تیگَنِشتی (بخارست)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی در جدول HFCC B26"
    },
    {
        "station_id": "STN-REE",
        "name_fa": "رادیو بین‌المللی اسپانیا (REE)",
        "name_en": "Radio Exterior de España",
        "country": "ESP",
        "country_fa": "اسپانیا",
        "broadcaster": "RTVE",
        "languages": ["es", "en", "ar"],
        "languages_fa": ["اسپانیایی", "انگلیسی", "عربی"],
        "category": "general",
        "category_fa": "فرهنگی و خبری",
        "sw_status": "active",
        "sw_status_fa": "فعال با فرستنده ۳۵۰ کیلووات نوبله‌خاس",
        "website": "https://www.rtve.es/radio/radio-exterior/",
        "description_fa": "رادیو برون‌مرزی ملی اسپانیا؛ اخبار اروپا، ایبرو-آمریکا، موسیقی و فرهنگ اسپانیایی با فرستنده مرکزی در نزدیکی مادرید.",
        "primary_transmitters_fa": "نوبله‌خاس (اسپانیا - ۳۵۰ کیلووات)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی در HFCC B26"
    },
    {
        "station_id": "STN-RTI",
        "name_fa": "رادیو تایوان بین‌المللی (RTI)",
        "name_en": "Radio Taiwan International",
        "country": "TWN",
        "country_fa": "تایوان",
        "broadcaster": "Radio Taiwan International",
        "languages": ["en", "zh"],
        "languages_fa": ["انگلیسی", "چینی"],
        "category": "general",
        "category_fa": "عمومی و خبری",
        "sw_status": "active",
        "sw_status_fa": "فعال در باندهای ۱۹، ۲۵ و ۳۱ متر",
        "website": "https://en.rti.org.tw",
        "description_fa": "صدای دموکراسی در شرق آسیا؛ پوشش رویدادهای تایوان، پیشرفت‌های فناوری و فرهنگ غنی چینی با زبان انگلیسی.",
        "primary_transmitters_fa": "کوگا / تینسی (تایوان - ۲۵۰ کیلووات)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: جدول فصلی HFCC B26"
    },
    {
        "station_id": "STN-KBS",
        "name_fa": "رادیو جهانی کی‌بی‌اس کره جنوبی (KBS World Radio)",
        "name_en": "KBS World Radio",
        "country": "KOR",
        "country_fa": "کره جنوبی",
        "broadcaster": "Korean Broadcasting System",
        "languages": ["en", "ar", "ru", "ko"],
        "languages_fa": ["انگلیسی", "عربی", "روسی", "کره‌ای"],
        "category": "general",
        "category_fa": "عمومی، فرهنگی و کی‌پاپ",
        "sw_status": "active",
        "sw_status_fa": "فعال با فرستنده‌های کیمجه",
        "website": "https://world.kbs.co.kr",
        "description_fa": "سرویس برون‌مرزی کره جنوبی؛ اخبار شبه‌جزیره کره، فرهنگ و هنر، صنعت و موسیقی کی‌پاپ به زبان‌های انگلیسی و عربی.",
        "primary_transmitters_fa": "کیمجه (کره جنوبی - ۲۵۰ کیلووات)، ووفِرتون (بریتانیا)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی در HFCC B26"
    },
    {
        "station_id": "STN-HISTORICAL-DW",
        "name_fa": "دویچه وله بخش فارسی (رادیو کلن - غیرفعال)",
        "name_en": "Deutsche Welle Persian (Historical - Closed)",
        "country": "DEU",
        "country_fa": "آلمان",
        "broadcaster": "Deutsche Welle",
        "languages": ["fa"],
        "languages_fa": ["فارسی"],
        "category": "historical",
        "category_fa": "تاریخی و غیرفعال",
        "sw_status": "inactive_historical",
        "sw_status_fa": "غیرفعال (تعطیل شده در زمستان ۲۰۱۱)",
        "website": "https://www.dw.com/fa",
        "description_fa": "بخش فارسی رادیو دویچه وله (رادیو کلن) پس از حدود ۵۰ سال فعالیت روی موج کوتاه، در دسامبر ۲۰۱۱ به دلیل مهاجرت به پلتفرم‌های اینترنتی تعطیل شد و هیچ پخش رادیویی فعالی روی امواج آنالوگ ندارد.",
        "primary_transmitters_fa": "سیکولینس (پرتغال) / ژولیخ (سابق)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: تأیید رسمی تعطیلی از سوی دویچه وله؛ درج جهت جلوگیری از اتلاف وقت کاربر"
    },
    {
        "station_id": "STN-HISTORICAL-RFI",
        "name_fa": "رادیو بین‌المللی فرانسه (RFI فارسی - غیرفعال)",
        "name_en": "Radio France Internationale Persian (Historical)",
        "country": "FRA",
        "country_fa": "فرانسه",
        "broadcaster": "France Médias Monde",
        "languages": ["fa"],
        "languages_fa": ["فارسی"],
        "category": "historical",
        "category_fa": "تاریخی و غیرفعال",
        "sw_status": "inactive_historical",
        "sw_status_fa": "غیرفعال روی موج کوتاه (فقط وب‌سایت)",
        "website": "https://www.rfi.fr/fa/",
        "description_fa": "پخش برنامه‌های رادیویی بخش فارسی ار‌اف‌ای روی موج کوتاه متوقف شده و فعالیت آن صرفاً به وب‌سایت خبری و پادکست‌های دیجیتال محدود است.",
        "primary_transmitters_fa": "ایسی‌سودان (سابق)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: تأیید تاریخی عدم فعالیت رادیویی آنالوگ"
    }
]

# ---------------------------------------------------------------------------
# SCHEDULES DATABASE (EACH RECORD IS A PRECISE TRANSMISSION SLOT)
# ---------------------------------------------------------------------------
RAW_SCHEDULES_DATA = [
    # --- 1. RADIO FARDA (ACTIVE PRIMARY SHORTWAVE & MW) ---
    {
        "station_id": "STN-FARDA",
        "program_title": "رادیو فردا: اخبار، گزارش و پخش زنده بامداد و صبحگاهی",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و تحلیلی",
        "frequency_khz": 5860,
        "modulation": "AM",
        "start_utc": "0000",
        "end_utc": "0600",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "الکبد (کویت)",
        "transmitter_site_code": "KWT",
        "transmitter_country": "کویت",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "50°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی (ثبت HFCC B26 و وبگاه رسمی)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت قطعی در هماهنگی رسمی اتحادیه مخابرات HFCC برای فصل زمستان B26 با توان ۲۵۰ کیلووات",
        "notes": "اصلی‌ترین فرکانس شبانگاهی و صبحگاهی رادیو فردا؛ سیگنال بسیار قدرتمند از کویت با پوشش کامل سراسر ایران."
    },
    {
        "station_id": "STN-FARDA",
        "program_title": "رادیو فردا: مجله نیمروزی و بعدازظهر",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و تحلیلی",
        "frequency_khz": 7435,
        "modulation": "AM",
        "start_utc": "1100",
        "end_utc": "1400",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "الکبد (کویت)",
        "transmitter_site_code": "KWT",
        "transmitter_country": "کویت",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "45°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت HFCC B26 و EiBi A26",
        "notes": "باند ۴۱ متر؛ انتشار بسیار خوب در بعدازظهر و تغییر نور خورشید."
    },
    {
        "station_id": "STN-FARDA",
        "program_title": "رادیو فردا: پخش زنده عصر و شامگاهی",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و تحلیلی",
        "frequency_khz": 9360,
        "modulation": "AM",
        "start_utc": "1400",
        "end_utc": "2300",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "الکبد (کویت)",
        "transmitter_site_code": "KWT",
        "transmitter_country": "کویت",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "50°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی HFCC B26 و EiBi",
        "notes": "یکی از پایدارترین فرکانس‌های رادیو فردا در باند ۳۱ متر برای ساعات ۱۷:۳۰ عصر تا ۰۲:۳۰ بامداد تهران."
    },
    {
        "station_id": "STN-FARDA",
        "program_title": "رادیو فردا: فرکانس مکمل شامگاهی (باند ۳۱ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و تحلیلی",
        "frequency_khz": 9370,
        "modulation": "AM",
        "start_utc": "1600",
        "end_utc": "2200",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "ووفِرتون (بریتانیا) / بیبلیس",
        "transmitter_site_code": "WO",
        "transmitter_country": "بریتانیا",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "95°",
        "target_area": "ایران و خاورمیانه",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده با چند منبع معتبر",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: فرکانس جایگزین ثبت‌شده برای مواقع پارازیت روی ۹۳۶۰ کیلوهرتز",
        "notes": "فرکانس کمکی برای فرار از تداخل‌های رادیویی محلی روی ۹۳۶۰ کیلوهرتز."
    },
    {
        "station_id": "STN-FARDA",
        "program_title": "رادیو فردا: برنامه روزانه (باند ۲۵ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و تحلیلی",
        "frequency_khz": 12005,
        "modulation": "AM",
        "start_utc": "0600",
        "end_utc": "1200",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "الکبد (کویت)",
        "transmitter_site_code": "KWT",
        "transmitter_country": "کویت",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "50°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: هماهنگی HFCC B26",
        "notes": "باند ۲۵ متر؛ فرکانس ایده‌آل روزانه برای ساعات صبح تا ظهر تهران (۰۹:۳۰ تا ۱۵:۳۰)."
    },
    {
        "station_id": "STN-FARDA",
        "program_title": "رادیو فردا: فرکانس جایگزین روزانه (باند ۲۵ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و تحلیلی",
        "frequency_khz": 12070,
        "modulation": "AM",
        "start_utc": "0800",
        "end_utc": "1500",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "بیبلیس (آلمان)",
        "transmitter_site_code": "D-bb",
        "transmitter_country": "آلمان",
        "transmitter_power_kw": 100,
        "azimuth_degrees": "105°",
        "target_area": "ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده با چند منبع معتبر",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ممیزی متقاطع HFCC و لاگ شنوندگان",
        "notes": "فرکانس پشتیبان برای نیمروز در فصول گرم و گذار پاییز."
    },
    {
        "station_id": "STN-FARDA",
        "program_title": "رادیو فردا: رله موج متوسط شمال و غرب ایران",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و تحلیلی",
        "frequency_khz": 864,
        "modulation": "AM",
        "start_utc": "1700",
        "end_utc": "2000",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "گاوار (ارمنستان)",
        "transmitter_site_code": "ARM",
        "transmitter_country": "ارمنستان",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "140°",
        "target_area": "شمال، مرکز و غرب ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "verified_multi_source",
        "status_fa": "تأییدشده در چند منبع تخصصی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ایستگاه پرقدرت ۵۰۰ کیلوواتی گاوار ارمنستان روی موج متوسط AM",
        "notes": "دریافت فوق‌العاده با هر رادیوی ساده خانگی یا رادیوی خودرو در استان‌های آذربایجان، کردستان، گیلان، مازندران و تهران (۲۰:۳۰ تا ۲۳:۳۰ به وقت تهران)."
    },
    {
        "station_id": "STN-FARDA",
        "program_title": "رادیو فردا: رله موج متوسط بعدازظهر",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و تحلیلی",
        "frequency_khz": 1395,
        "modulation": "AM",
        "start_utc": "1500",
        "end_utc": "1700",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "گاوار (ارمنستان)",
        "transmitter_site_code": "ARM",
        "transmitter_country": "ارمنستان",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "140°",
        "target_area": "شمال و غرب ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "verified_multi_source",
        "status_fa": "تأییدشده در چند منبع تخصصی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: تایید در لاگ‌های EiBi و گزارش‌های میدانی DX",
        "notes": "ساعت ۱۸:۳۰ تا ۲۰:۳۰ به وقت تهران روی باند موج متوسط AM."
    },

    # --- 2. CHINA RADIO INTERNATIONAL (CRI PERSIAN) ---
    {
        "station_id": "STN-CRI",
        "program_title": "رادیو بین‌المللی چین: برنامه شامگاهی بخش فارسی (نوبت اول)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "general",
        "category_fa": "عمومی، خبری و فرهنگی",
        "frequency_khz": 7415,
        "modulation": "AM",
        "start_utc": "1800",
        "end_utc": "1900",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "شی‌آن (چین)",
        "transmitter_site_code": "XIA",
        "transmitter_country": "چین",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "278°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی (ثبت HFCC B26 و وبگاه رسمی CRI)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: فرستنده ۵۰۰ کیلوواتی با قدرت خیره‌کننده و ثبت بین‌المللی",
        "notes": "ساعت ۲۱:۳۰ تا ۲۲:۳۰ به وقت تهران. از رساترین و باکیفیت‌ترین سیگنال‌های رادیویی موج کوتاه در تمام ایران."
    },
    {
        "station_id": "STN-CRI",
        "program_title": "رادیو بین‌المللی چین: برنامه بعدازظهر بخش فارسی (باند ۳۱ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "general",
        "category_fa": "عمومی، خبری و فرهنگی",
        "frequency_khz": 9570,
        "modulation": "AM",
        "start_utc": "1500",
        "end_utc": "1530",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "ارومچی (چین)",
        "transmitter_site_code": "UR",
        "transmitter_country": "چین",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "260°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت HFCC B26 و وب‌سایت CRI",
        "notes": "ساعت ۱۸:۳۰ تا ۱۹:۰۰ به وقت تهران."
    },
    {
        "station_id": "STN-CRI",
        "program_title": "رادیو بین‌المللی چین: فرکانس موازی بعدازظهر (باند ۳۱ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "general",
        "category_fa": "عمومی، خبری و فرهنگی",
        "frequency_khz": 9600,
        "modulation": "AM",
        "start_utc": "1500",
        "end_utc": "1530",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "کاشغر (سین‌کیانگ)",
        "transmitter_site_code": "KAS",
        "transmitter_country": "چین",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "260°",
        "target_area": "ایران و خاورمیانه",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت HFCC B26",
        "notes": "پخش همزمان با ۹۵۷۰ کیلوهرتز؛ در صورت افت سیگنال در یکی، دیگری را بگیرید."
    },
    {
        "station_id": "STN-CRI",
        "program_title": "رادیو بین‌المللی چین: فرکانس موازی شامگاهی (باند ۳۱ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "general",
        "category_fa": "عمومی، خبری و فرهنگی",
        "frequency_khz": 9670,
        "modulation": "AM",
        "start_utc": "1800",
        "end_utc": "1830",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "پکن (چین)",
        "transmitter_site_code": "BEI",
        "transmitter_country": "چین",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "285°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت HFCC B26",
        "notes": "پخش موازی با ۷۴۱۵ کیلوهرتز در ساعت ۲۱:۳۰ تا ۲۲:۰۰ تهران."
    },
    {
        "station_id": "STN-CRI",
        "program_title": "رادیو بین‌المللی چین: بازپخش شامگاهی (باند ۴۱ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "general",
        "category_fa": "عمومی، خبری و فرهنگی",
        "frequency_khz": 7325,
        "modulation": "AM",
        "start_utc": "1800",
        "end_utc": "1900",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "پکن (چین)",
        "transmitter_site_code": "BEI",
        "transmitter_country": "چین",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "285°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی (ثبت جدول زمستان B26)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی در جدول جدید B26 کنفرانس HFCC",
        "notes": "فرکانس جدید هماهنگ‌شده برای فصل سرما در ساعت ۲۱:۳۰ تا ۲۲:۳۰ تهران."
    },

    # --- 3. VOICE OF TURKEY (TRT PERSIAN) ---
    {
        "station_id": "STN-TRT",
        "program_title": "صدای ترکیه: برنامه غروبگاهی بخش فارسی",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "general",
        "category_fa": "عمومی، خبری و منطقه‌ای",
        "frequency_khz": 9765,
        "modulation": "AM",
        "start_utc": "1500",
        "end_utc": "1600",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "امیرلر (ترکیه)",
        "transmitter_site_code": "EMR",
        "transmitter_country": "ترکیه",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "110°",
        "target_area": "ایران و خاورمیانه (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-TRT-OFFICIAL",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی (ثبت HFCC و TRT Farsi)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: فرستنده عظیم ۵۰۰ کیلوواتی امیرلر ترکیه مستقیماً رو به ایران",
        "notes": "ساعت ۱۸:۳۰ تا ۱۹:۳۰ به وقت تهران. وضوح سیگنال در غرب و مرکز ایران بسیار عالی است."
    },
    {
        "station_id": "STN-TRT",
        "program_title": "صدای ترکیه: فرکانس زمستانه بخش فارسی (باند ۳۱ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "general",
        "category_fa": "عمومی، خبری و منطقه‌ای",
        "frequency_khz": 9490,
        "modulation": "AM",
        "start_utc": "1600",
        "end_utc": "1700",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "امیرلر (ترکیه)",
        "transmitter_site_code": "EMR",
        "transmitter_country": "ترکیه",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "110°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی در جدول B26",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت در هماهنگی رسمی اتحادیه مخابرات برای فصل زمستان",
        "notes": "ساعت ۱۹:۳۰ تا ۲۰:۳۰ به وقت تهران با توان ۵۰۰ کیلووات."
    },
    {
        "station_id": "STN-TRT",
        "program_title": "صدای ترکیه: برنامه نیمروزی بخش فارسی (باند ۱۹ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "general",
        "category_fa": "عمومی، خبری و منطقه‌ای",
        "frequency_khz": 15720,
        "modulation": "AM",
        "start_utc": "0830",
        "end_utc": "1000",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "امیرلر (ترکیه)",
        "transmitter_site_code": "EMR",
        "transmitter_country": "ترکیه",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "110°",
        "target_area": "ایران و خاورمیانه",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-TRT-OFFICIAL",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت در EiBi و پایگاه رسمی صدای ترکیه",
        "notes": "ساعت ۱۲:۰۰ تا ۱۳:۳۰ ظهر به وقت تهران؛ باند ۱۹ متر با دریافت شفاف روزانه."
    },
    {
        "station_id": "STN-TRT",
        "program_title": "صدای ترکیه: فرکانس روزانه فصول سرد (باند ۲۲ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "general",
        "category_fa": "عمومی، خبری و منطقه‌ای",
        "frequency_khz": 13745,
        "modulation": "AM",
        "start_utc": "0930",
        "end_utc": "1100",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "امیرلر (ترکیه)",
        "transmitter_site_code": "EMR",
        "transmitter_country": "ترکیه",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "110°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی B26",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت HFCC B26",
        "notes": "ساعت ۱۳:۰۰ تا ۱۴:۳۰ به وقت تهران."
    },

    # --- 4. ALL INDIA RADIO (AIR AKASHVANI PERSIAN) ---
    {
        "station_id": "STN-AIR",
        "program_title": "رادیو هند (آکاشوانی): برنامه شبانگاهی بخش فارسی",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "culture",
        "category_fa": "فرهنگی، موسیقی و خبری",
        "frequency_khz": 9620,
        "modulation": "AM",
        "start_utc": "1600",
        "end_utc": "1730",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "بنگالورو (هند)",
        "transmitter_site_code": "BG",
        "transmitter_country": "هند",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "305°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-AIR-OFFICIAL",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی (پراسار بهاراتی و HFCC)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: تایید در جدول رسمی دولتی هند و لاگ‌های EiBi",
        "notes": "ساعت ۱۹:۳۰ تا ۲۱:۰۰ به وقت تهران. شامل اخبار دهلی، موسیقی سنتی و معرفی کتاب و فرهنگ."
    },
    {
        "station_id": "STN-AIR",
        "program_title": "رادیو هند (آکاشوانی): برنامه صبحگاهی بخش فارسی",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "culture",
        "category_fa": "فرهنگی، موسیقی و خبری",
        "frequency_khz": 15130,
        "modulation": "AM",
        "start_utc": "0400",
        "end_utc": "0530",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "بنگالورو (هند)",
        "transmitter_site_code": "BG",
        "transmitter_country": "هند",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "305°",
        "target_area": "ایران و افغانستان",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-AIR-OFFICIAL",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت در هماهنگی HFCC B26 و EiBi",
        "notes": "ساعت ۰۷:۳۰ تا ۰۹:۰۰ صبح به وقت تهران روی باند ۱۹ متر."
    },
    {
        "station_id": "STN-AIR",
        "program_title": "رادیو هند: فرکانس تکمیلی شامگاهی (باند ۲۵ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "culture",
        "category_fa": "فرهنگی، موسیقی و خبری",
        "frequency_khz": 11905,
        "modulation": "AM",
        "start_utc": "1600",
        "end_utc": "1730",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "بنگالورو (هند)",
        "transmitter_site_code": "BG",
        "transmitter_country": "هند",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "305°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی B26",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت در جدول HFCC B26",
        "notes": "ساعت ۱۹:۳۰ تا ۲۱:۰۰ تهران به عنوان فرکانس پشتیبان ۹۶۲۰ کیلوهرتز."
    },

    # --- 5. NHK WORLD-JAPAN (PERSIAN) ---
    {
        "station_id": "STN-NHK",
        "program_title": "رادیو ژاپن (NHK World): برنامه شامگاهی بخش فارسی",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "general",
        "category_fa": "عمومی، علمی و فرهنگی",
        "frequency_khz": 13600,
        "modulation": "AM",
        "start_utc": "1630",
        "end_utc": "1650",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "یاماتا (ژاپن)",
        "transmitter_site_code": "YA",
        "transmitter_country": "ژاپن",
        "transmitter_power_kw": 300,
        "azimuth_degrees": "295°",
        "target_area": "ایران و خاورمیانه",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-NHK-OFFICIAL",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی (ان‌اچ‌کی ژاپن و EiBi)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: فرستنده پرقدرت ۳۰۰ کیلوواتی یاماتا در استان ایباراکی ژاپن",
        "notes": "ساعت ۲۰:۰۰ تا ۲۰:۲۰ به وقت تهران. برنامه ۲۰ دقیقه‌ای فشرده شامل اخبار توکیو و درس ژاپنی."
    },
    {
        "station_id": "STN-NHK",
        "program_title": "رادیو ژاپن: فرکانس زمستانه بخش فارسی (باند ۳۱ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "general",
        "category_fa": "عمومی، علمی و فرهنگی",
        "frequency_khz": 9600,
        "modulation": "AM",
        "start_utc": "1630",
        "end_utc": "1650",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "یاماتا (ژاپن)",
        "transmitter_site_code": "YA",
        "transmitter_country": "ژاپن",
        "transmitter_power_kw": 300,
        "azimuth_degrees": "295°",
        "target_area": "ایران و خاورمیانه (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی B26",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی HFCC B26",
        "notes": "ساعت ۲۰:۰۰ تا ۲۰:۲۰ به وقت تهران با کیفیت بسیار بالا در فصول سرد."
    },
    {
        "station_id": "STN-NHK",
        "program_title": "رادیو ژاپن: رله پرقدرت موج متوسط از تاجیکستان",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "general",
        "category_fa": "عمومی، علمی و فرهنگی",
        "frequency_khz": 1251,
        "modulation": "AM",
        "start_utc": "1630",
        "end_utc": "1650",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "دوشنبه / اورزو (تاجیکستان)",
        "transmitter_site_code": "TJK",
        "transmitter_country": "تاجیکستان",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "240°",
        "target_area": "شمال شرق، شرق و مرکز ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "verified_multi_source",
        "status_fa": "تأییدشده در چند منبع تخصصی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت در EiBi و وبگاه رسمی ان‌اچ‌کی",
        "notes": "ساعت ۲۰:۰۰ تا ۲۰:۲۰ تهران؛ قابل دریافت روی موج متوسط AM با رادیوهای معمولی به ویژه در خراسان، سمنان، سیستان و تهران."
    },

    # --- 6. RADIO KUWAIT (PERSIAN) ---
    {
        "station_id": "STN-KUWAIT",
        "program_title": "رادیو کویت: برنامه نیمروزی بخش فارسی",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "general",
        "category_fa": "عمومی، مذهبی و منطقه‌ای",
        "frequency_khz": 7250,
        "modulation": "AM",
        "start_utc": "0800",
        "end_utc": "1000",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "الکبد (کویت)",
        "transmitter_site_code": "KWT",
        "transmitter_country": "کویت",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "45°",
        "target_area": "ایران و حوزه خلیج فارس (CIRAF 39-40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی (ثبت وزارت اطلاع‌رسانی کویت و HFCC)",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: فرستنده پرقدرت الکبد با هدایت مستقیم سیگنال روی غرب و جنوب ایران",
        "notes": "ساعت ۱۱:۳۰ تا ۱۳:۳۰ به وقت تهران. دریافت بسیار شفاف در خوزستان، بوشهر، فارس، لرستان و مرکز ایران."
    },

    # --- 7. IRAN INTERNATIONAL (SHORTWAVE AUDIO RELAY) ---
    {
        "station_id": "STN-IRAN-INTL",
        "program_title": "ایران اینترنشنال: رله صوتی شبانگاهی موج کوتاه (فرکانس اصلی)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و اطلاع‌رسانی اضطراری",
        "frequency_khz": 5890,
        "modulation": "AM",
        "start_utc": "1900",
        "end_utc": "0400",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "کوستینبرود (بلغارستان - اسپیس‌لاین)",
        "transmitter_site_code": "BUL",
        "transmitter_country": "بلغارستان",
        "transmitter_power_kw": 100,
        "azimuth_degrees": "105°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "verified_multi_source",
        "status_fa": "تأییدشده در چند منبع تخصصی (EiBi و لاگ‌های شنوندگان)",
        "confidence_level": "B",
        "confidence_description_fa": "سطح B: رله ماهواره‌ای از طریق امکانات پخش اسپیس‌لاین در اروپای شرقی",
        "notes": "ساعت ۲۲:۳۰ تا ۰۷:۳۰ صبح روز بعد به وقت تهران؛ مناسب برای پیگیری اخبار در زمان قطع شبانه اینترنت."
    },
    {
        "station_id": "STN-IRAN-INTL",
        "program_title": "ایران اینترنشنال: فرکانس موازی رله شبانگاهی (باند ۴۹ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و اطلاع‌رسانی اضطراری",
        "frequency_khz": 5900,
        "modulation": "AM",
        "start_utc": "1900",
        "end_utc": "0400",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "کوستینبرود (بلغارستان - اسپیس‌لاین)",
        "transmitter_site_code": "BUL",
        "transmitter_country": "بلغارستان",
        "transmitter_power_kw": 100,
        "azimuth_degrees": "105°",
        "target_area": "ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "verified_multi_source",
        "status_fa": "تأییدشده در چند منبع تخصصی",
        "confidence_level": "B",
        "confidence_description_fa": "سطح B: تایید در دایرکتوری EiBi و مانیتورینگ WebSDR",
        "notes": "پخش موازی با ۵۸۹۰ کیلوهرتز؛ ساعت ۲۲:۳۰ تا ۰۷:۳۰ به وقت تهران."
    },
    {
        "station_id": "STN-IRAN-INTL",
        "program_title": "ایران اینترنشنال: رله موج متوسط شمال ایران",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و اطلاع‌رسانی اضطراری",
        "frequency_khz": 864,
        "modulation": "AM",
        "start_utc": "2000",
        "end_utc": "2300",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "گاوار (ارمنستان)",
        "transmitter_site_code": "ARM",
        "transmitter_country": "ارمنستان",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "140°",
        "target_area": "شمال، آذربایجان و تهران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "verified_multi_source",
        "status_fa": "تأییدشده در چند منبع تخصصی",
        "confidence_level": "B",
        "confidence_description_fa": "سطح B: پخش موج متوسط از ارمنستان پس از پایان شیفت رادیو فردا",
        "notes": "ساعت ۲۳:۳۰ تا ۰۲:۳۰ بامداد تهران روی موج متوسط AM با رادیوهای معمولی."
    },

    # --- 8. RADIO ZAMANEH ---
    {
        "station_id": "STN-ZAMANEH",
        "program_title": "رادیو زمانه: برنامه شبانگاهی مجله اجتماعی و فرهنگی",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "culture",
        "category_fa": "اجتماعی، فرهنگی و تحلیلی",
        "frequency_khz": 6010,
        "modulation": "AM",
        "start_utc": "1930",
        "end_utc": "2030",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "کوستینبرود (بلغارستان - اسپیس‌لاین)",
        "transmitter_site_code": "BUL",
        "transmitter_country": "بلغارستان",
        "transmitter_power_kw": 100,
        "azimuth_degrees": "105°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "verified_multi_source",
        "status_fa": "تأییدشده در چند منبع تخصصی (EiBi)",
        "confidence_level": "B",
        "confidence_description_fa": "سطح B: ثبت در دایرکتوری EiBi و سابقه پخش ثابت در باند ۴۹ متر",
        "notes": "ساعت ۲۳:۰۰ تا ۰۰:۰۰ نیمه‌شب به وقت تهران در باند ۴۹ متر."
    },

    # --- 9. VOA PERSIAN (MW 24H) ---
    {
        "station_id": "STN-VOA-PERSIAN",
        "program_title": "صدای آمریکا: پخش ۲۴ ساعته موج متوسط خاورمیانه",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و سیاسی",
        "frequency_khz": 1548,
        "modulation": "AM",
        "start_utc": "0000",
        "end_utc": "2400",
        "days": "1234567",
        "days_fa": "روزانه (۲۴ ساعته)",
        "transmitter_site": "الکبد (کویت)",
        "transmitter_site_code": "KWT",
        "transmitter_country": "کویت",
        "transmitter_power_kw": 600,
        "azimuth_degrees": "40°",
        "target_area": "ایران و خلیج فارس",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: یکی از قوی‌ترین فرستنده‌های موج متوسط خاورمیانه با توان ۶۰۰ کیلووات",
        "notes": "پخش شبانه‌روزی برنامه‌های VOA Persian و بخش‌های رادیو فردا با پوشش فوق‌العاده در تمام فلات ایران روی گیرنده‌های ساده AM."
    },

    # --- 10. BBC PERSIAN (EMERGENCY / RELAY STATUS) ---
    {
        "station_id": "STN-BBC-PERSIAN",
        "program_title": "رادیو فارسی بی‌بی‌سی: فرکانس رله اضطراری موج کوتاه (باند ۴۹ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و تحلیلی",
        "frequency_khz": 6000,
        "modulation": "AM",
        "start_utc": "1630",
        "end_utc": "1700",
        "days": "1234567",
        "days_fa": "روزانه در ایام بحران",
        "transmitter_site": "ترینکومالی (سری‌لانکا)",
        "transmitter_site_code": "SL",
        "transmitter_country": "سری‌لانکا",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "325°",
        "target_area": "ایران (CIRAF 40)",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "emergency_relay",
        "status_fa": "پخش اضطراری و مقطعی (نیازمند بررسی فعال بودن)",
        "confidence_level": "C",
        "confidence_description_fa": "سطح C: رزرو فرکانس در هماهنگی بین‌المللی HFCC B26 برای شرایط بحرانی پس از تعطیلی بخش عادی",
        "notes": "ساعت ۲۰:۰۰ تا ۲۰:۳۰ تهران. بخش عادی رادیو فارسی بی‌بی‌سی تعطیل شده، اما در زمان جنگ، بحران یا قطع اینترنت بین‌الملل فعال می‌شود."
    },
    {
        "station_id": "STN-BBC-PERSIAN",
        "program_title": "رادیو فارسی بی‌بی‌سی: رله موج متوسط خلیج فارس و جنوب ایران",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و تحلیلی",
        "frequency_khz": 702,
        "modulation": "AM",
        "start_utc": "1630",
        "end_utc": "1700",
        "days": "1234567",
        "days_fa": "روزانه در ایام بحران",
        "transmitter_site": "الاشخره (عمان)",
        "transmitter_site_code": "OMA",
        "transmitter_country": "عمان",
        "transmitter_power_kw": 800,
        "azimuth_degrees": "345°",
        "target_area": "جنوب و مرکز ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "emergency_relay",
        "status_fa": "پخش اضطراری / رزرو موج متوسط",
        "confidence_level": "C",
        "confidence_description_fa": "سطح C: فرستنده عظیم ۸۰۰ کیلوواتی بی‌بی‌سی در عمان برای پخش اضطراری",
        "notes": "ساعت ۲۰:۰۰ تا ۲۰:۳۰ تهران روی موج متوسط ۷۰۲ کیلوهرتز."
    },
    {
        "station_id": "STN-BBC-PERSIAN",
        "program_title": "رادیو فارسی بی‌بی‌سی: رله موج متوسط قبرس",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "news",
        "category_fa": "خبری و تحلیلی",
        "frequency_khz": 720,
        "modulation": "AM",
        "start_utc": "1630",
        "end_utc": "1700",
        "days": "1234567",
        "days_fa": "روزانه در ایام بحران",
        "transmitter_site": "زیگی (قبرس)",
        "transmitter_site_code": "CYP",
        "transmitter_country": "قبرس",
        "transmitter_power_kw": 300,
        "azimuth_degrees": "85°",
        "target_area": "غرب و مرکز ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "emergency_relay",
        "status_fa": "پخش اضطراری / رزرو موج متوسط",
        "confidence_level": "C",
        "confidence_description_fa": "سطح C: فرستنده اختصاصی رله خاورمیانه بی‌بی‌سی در قبرس",
        "notes": "ساعت ۲۰:۰۰ تا ۲۰:۳۰ به وقت تهران روی ۷۲۰ کیلوهرتز موج متوسط."
    },

    # --- 11. OPPOSITION & CLANDESTINE SW BROADCASTS ---
    {
        "station_id": "STN-OPPOSITION-CLANDESTINE",
        "program_title": "رادیو پیام (چپ / کارگری و دانشجویی)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "opposition",
        "category_fa": "سیاسی و اپوزیسیون",
        "frequency_khz": 9310,
        "modulation": "AM",
        "start_utc": "1730",
        "end_utc": "1930",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "فرستنده اجاره‌ای اروپای شرقی",
        "transmitter_site_code": "XUU",
        "transmitter_country": "بین‌المللی",
        "transmitter_power_kw": 100,
        "azimuth_degrees": "100°",
        "target_area": "ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "single_source_reported",
        "status_fa": "گزارش‌شده در منابع تخصصی مانیتورینگ",
        "confidence_level": "C",
        "confidence_description_fa": "سطح C: ایستگاه‌های سیاسی زیرزمینی که فرستنده‌های تجاری را در بازه‌های کوتاه اجاره می‌کنند",
        "notes": "ساعت ۲۱:۰۰ تا ۲۳:۰۰ به وقت تهران در باند ۳۱ متر."
    },
    {
        "station_id": "STN-OPPOSITION-CLANDESTINE",
        "program_title": "رادیو پیام: فرکانس جایگزین شامگاهی",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "opposition",
        "category_fa": "سیاسی و اپوزیسیون",
        "frequency_khz": 11815,
        "modulation": "AM",
        "start_utc": "1700",
        "end_utc": "2100",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "ووفِرتون (بریتانیا)",
        "transmitter_site_code": "WO",
        "transmitter_country": "بریتانیا",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "95°",
        "target_area": "ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "single_source_reported",
        "status_fa": "گزارش‌شده در منبع تخصصی",
        "confidence_level": "C",
        "confidence_description_fa": "سطح C: ثبت در لاگ‌های EiBi",
        "notes": "ساعت ۲۰:۳۰ تا ۰۰:۳۰ بامداد روز بعد به وقت تهران روی باند ۲۵ متر."
    },
    {
        "station_id": "STN-OPPOSITION-CLANDESTINE",
        "program_title": "صدای مجاهد (رادیو مجاهدین خلق)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "opposition",
        "category_fa": "سیاسی و اپوزیسیون",
        "frequency_khz": 9320,
        "modulation": "AM",
        "start_utc": "1700",
        "end_utc": "1730",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "فرستنده اجاره‌ای متغیر",
        "transmitter_site_code": "XUU",
        "transmitter_country": "بین‌المللی",
        "transmitter_power_kw": 100,
        "azimuth_degrees": "100°",
        "target_area": "ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "single_source_reported",
        "status_fa": "گزارش‌شده در منابع تخصصی DX",
        "confidence_level": "C",
        "confidence_description_fa": "سطح C: پخش کوتاه ۳۰ دقیقه‌ای با هدف انتشار اطلاعیه‌ها و سرودهای سازمانی",
        "notes": "ساعت ۲۰:۳۰ تا ۲۱:۰۰ به وقت تهران."
    },
    {
        "station_id": "STN-OPPOSITION-CLANDESTINE",
        "program_title": "رادیو براندازی",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "opposition",
        "category_fa": "سیاسی و اپوزیسیون",
        "frequency_khz": 11945,
        "modulation": "AM",
        "start_utc": "1330",
        "end_utc": "1430",
        "days": "Tu,Fr",
        "days_fa": "سه‌شنبه و جمعه",
        "transmitter_site": "فرستنده متغیر",
        "transmitter_site_code": "XUU",
        "transmitter_country": "بین‌المللی",
        "transmitter_power_kw": 100,
        "azimuth_degrees": "95°",
        "target_area": "ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "single_source_reported",
        "status_fa": "گزارش‌شده در منبع تخصصی (روزهای مشخص)",
        "confidence_level": "C",
        "confidence_description_fa": "سطح C: پخش هفتگی متناوب",
        "notes": "ساعت ۱۷:۰۰ تا ۱۸:۰۰ عصر به وقت تهران."
    },

    # --- 12. RELIGIOUS & CULTURAL BROADCASTS ---
    {
        "station_id": "STN-RELIGIOUS-TWR-BV",
        "program_title": "رادیو مژده (ترانس ورلد رادیو / بخش فارسی)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "religious",
        "category_fa": "مذهبی و نیایشی",
        "frequency_khz": 1377,
        "modulation": "AM",
        "start_utc": "1800",
        "end_utc": "1930",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "گاوار (ارمنستان)",
        "transmitter_site_code": "ARM",
        "transmitter_country": "ارمنستان",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "140°",
        "target_area": "ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "verified_multi_source",
        "status_fa": "تأییدشده در چند منبع تخصصی",
        "confidence_level": "B",
        "confidence_description_fa": "سطح B: فرستنده پرقدرت موج متوسط با ثبت سابقه منظم",
        "notes": "ساعت ۲۱:۳۰ تا ۲۳:۰۰ به وقت تهران روی موج متوسط AM با گیرنده‌های ساده."
    },
    {
        "station_id": "STN-RELIGIOUS-TWR-BV",
        "program_title": "صدای انجیل (Bible Voice بخش فارسی - باند ۳۱ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "religious",
        "category_fa": "مذهبی و نیایشی",
        "frequency_khz": 9400,
        "modulation": "AM",
        "start_utc": "1800",
        "end_utc": "1830",
        "days": "Th-Fr",
        "days_fa": "پنج‌شنبه و جمعه",
        "transmitter_site": "کوستینبرود (بلغارستان)",
        "transmitter_site_code": "BUL",
        "transmitter_country": "بلغارستان",
        "transmitter_power_kw": 100,
        "azimuth_degrees": "105°",
        "target_area": "خاورمیانه و ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "verified_multi_source",
        "status_fa": "تأییدشده در دایرکتوری تخصصی",
        "confidence_level": "B",
        "confidence_description_fa": "سطح B: تایید در لاگ‌های EiBi",
        "notes": "ساعت ۲۱:۳۰ تا ۲۲:۰۰ تهران."
    },
    {
        "station_id": "STN-RELIGIOUS-TWR-BV",
        "program_title": "صدای انجیل (Bible Voice بخش فارسی - باند ۲۵ متر)",
        "language": "fa",
        "language_fa": "فارسی",
        "category": "religious",
        "category_fa": "مذهبی و نیایشی",
        "frequency_khz": 11855,
        "modulation": "AM",
        "start_utc": "1800",
        "end_utc": "1830",
        "days": "Su-Tu",
        "days_fa": "یک‌شنبه تا سه‌شنبه",
        "transmitter_site": "نائن (آلمان)",
        "transmitter_site_code": "D-n",
        "transmitter_country": "آلمان",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "115°",
        "target_area": "خاورمیانه و ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-EIBI-A26",
        "status": "verified_multi_source",
        "status_fa": "تأییدشده در چند منبع تخصصی",
        "confidence_level": "B",
        "confidence_description_fa": "سطح B: فرستنده پرقدرت ۵۰۰ کیلوواتی نائن آلمان",
        "notes": "ساعت ۲۱:۳۰ تا ۲۲:۰۰ تهران."
    },

    # --- 13. IRIB EXTERNAL SERVICES (VOICE OF I.R. IRAN) ---
    {
        "station_id": "STN-IRIB-VOIRI",
        "program_title": "صدای جمهوری اسلامی ایران: سرویس دری (ویژه افغانستان)",
        "language": "dr",
        "language_fa": "دری (فارسی شرقی)",
        "category": "general",
        "category_fa": "عمومی، خبری و منطقه‌ای",
        "frequency_khz": 720,
        "modulation": "AM",
        "start_utc": "0320",
        "end_utc": "1520",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "تایباد / شرق ایران",
        "transmitter_site_code": "IRN",
        "transmitter_country": "ایران",
        "transmitter_power_kw": 200,
        "azimuth_degrees": "80°",
        "target_area": "افغانستان و شرق ایران",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی HFCC B26 و IRIB",
        "notes": "ساعت ۰۶:۵۰ تا ۱۸:۵۰ به وقت تهران روی موج متوسط؛ زبان دری برای شنوندگان داخل ایران کاملاً مفهوم است."
    },
    {
        "station_id": "STN-IRIB-VOIRI",
        "program_title": "صدای جمهوری اسلامی ایران: برنامه تاجیکی (موج کوتاه باند ۴۹ متر)",
        "language": "tj",
        "language_fa": "تاجیکی (فارسی ماوراءالنهر)",
        "category": "general",
        "category_fa": "عمومی، فرهنگی و منطقه‌ای",
        "frequency_khz": 6000,
        "modulation": "AM",
        "start_utc": "0050",
        "end_utc": "0220",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "سیرجان (کرمان)",
        "transmitter_site_code": "IRN-S",
        "transmitter_country": "ایران",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "45°",
        "target_area": "آسیای مرکزی و تاجیکستان",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: فرستنده ۵۰۰ کیلوواتی سیرجان ثبت در HFCC B26",
        "notes": "ساعت ۰۴:۲۰ تا ۰۵:۵۰ صبح به وقت تهران. زبان تاجیکی لهجه‌ای از پارسی است و برای شنوندگان فارسی‌زبان کاملاً قابل درک است."
    },
    {
        "station_id": "STN-IRIB-VOIRI",
        "program_title": "صدای جمهوری اسلامی ایران: برنامه کردی (باند ۳۱ متر)",
        "language": "ku",
        "language_fa": "کردی (سورانی)",
        "category": "general",
        "category_fa": "عمومی و منطقه‌ای",
        "frequency_khz": 9715,
        "modulation": "AM",
        "start_utc": "1320",
        "end_utc": "1420",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "سیرجان (کرمان)",
        "transmitter_site_code": "IRN-S",
        "transmitter_country": "ایران",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "285°",
        "target_area": "خاورمیانه، کردستان و عراق",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت HFCC B26",
        "notes": "ساعت ۱۶:۵۰ تا ۱۷:۵۰ به وقت تهران با توان ۵۰۰ کیلووات."
    },
    {
        "station_id": "STN-IRIB-VOIRI",
        "program_title": "صدای جمهوری اسلامی ایران: سرویس انگلیسی برون‌مرزی (باند ۳۱ متر)",
        "language": "en",
        "language_fa": "انگلیسی",
        "category": "news",
        "category_fa": "خبری و تحلیلی بین‌المللی",
        "frequency_khz": 9830,
        "modulation": "AM",
        "start_utc": "1920",
        "end_utc": "2020",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "سیرجان (کرمان)",
        "transmitter_site_code": "IRN-S",
        "transmitter_country": "ایران",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "210°",
        "target_area": "آفریقا و خاورمیانه",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: فرستنده ۵۰۰ کیلوواتی سیرجان",
        "notes": "ساعت ۲۲:۵۰ تا ۲۳:۵۰ به وقت تهران."
    },

    # --- 14. MAJOR INTERNATIONAL SERVICES (ENGLISH & MAJOR LANGUAGES) ---
    {
        "station_id": "STN-BBC-WS-EN",
        "program_title": "سرویس جهانی بی‌بی‌سی: اخبار جهانی به زبان انگلیسی (باند ۴۹ متر)",
        "language": "en",
        "language_fa": "انگلیسی",
        "category": "news",
        "category_fa": "بین‌المللی و خبری",
        "frequency_khz": 6195,
        "modulation": "AM",
        "start_utc": "0400",
        "end_utc": "0700",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "زیگی (قبرس)",
        "transmitter_site_code": "CYP",
        "transmitter_country": "قبرس",
        "transmitter_power_kw": 300,
        "azimuth_degrees": "95°",
        "target_area": "خاورمیانه و غرب آسیا",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی در جدول HFCC B26 و BBC World Service",
        "notes": "ساعت ۰۷:۳۰ تا ۱۰:۳۰ صبح به وقت تهران. پوشش عالی اخبار جهانی در زمان قطع اینترنت."
    },
    {
        "station_id": "STN-BBC-WS-EN",
        "program_title": "سرویس جهانی بی‌بی‌سی: اخبار بین‌المللی انگلیسی (باند ۳۱ متر)",
        "language": "en",
        "language_fa": "انگلیسی",
        "category": "news",
        "category_fa": "بین‌المللی و خبری",
        "frequency_khz": 9410,
        "modulation": "AM",
        "start_utc": "1500",
        "end_utc": "1800",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "ووفِرتون (بریتانیا)",
        "transmitter_site_code": "WO",
        "transmitter_country": "بریتانیا",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "105°",
        "target_area": "خاورمیانه و آسیا",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی HFCC B26",
        "notes": "ساعت ۱۸:۳۰ تا ۲۱:۳۰ شب به وقت تهران؛ از مطمئن‌ترین فرکانس‌های خبری انگلیسی در منطقه."
    },
    {
        "station_id": "STN-BBC-WS-EN",
        "program_title": "سرویس جهانی بی‌بی‌سی: برنامه روزانه انگلیسی (باند ۲۵ متر)",
        "language": "en",
        "language_fa": "انگلیسی",
        "category": "news",
        "category_fa": "بین‌المللی و خبری",
        "frequency_khz": 12095,
        "modulation": "AM",
        "start_utc": "0700",
        "end_utc": "1500",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "الاشخره (عمان)",
        "transmitter_site_code": "OMA",
        "transmitter_country": "عمان",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "350°",
        "target_area": "ایران، خلیج فارس و خاورمیانه",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت در HFCC B26",
        "notes": "ساعت ۱۰:۳۰ صبح تا ۱۸:۳۰ عصر به وقت تهران با کیفیت بسیار بالا."
    },
    {
        "station_id": "STN-BBC-WS-EN",
        "program_title": "بی‌بی‌سی عربی: پخش اخبار جهان عرب و منطقه (باند ۳۱ متر)",
        "language": "ar",
        "language_fa": "عربی",
        "category": "news",
        "category_fa": "خبری و منطقه‌ای",
        "frequency_khz": 9830,
        "modulation": "AM",
        "start_utc": "0400",
        "end_utc": "0600",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "زیگی (قبرس)",
        "transmitter_site_code": "CYP",
        "transmitter_country": "قبرس",
        "transmitter_power_kw": 300,
        "azimuth_degrees": "110°",
        "target_area": "خاورمیانه و خلیج فارس",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: هماهنگی HFCC B26",
        "notes": "ساعت ۰۷:۳۰ تا ۰۹:۳۰ صبح تهران. پوشش جامع رویدادهای خاورمیانه به زبان عربی فصیح."
    },
    {
        "station_id": "STN-VOA-EN",
        "program_title": "صدای آمریکا: اخبار انگلیسی VOA News Now (باند ۲۵ متر)",
        "language": "en",
        "language_fa": "انگلیسی",
        "category": "news",
        "category_fa": "بین‌المللی و خبری",
        "frequency_khz": 12025,
        "modulation": "AM",
        "start_utc": "0300",
        "end_utc": "0600",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "الکبد (کویت)",
        "transmitter_site_code": "KWT",
        "transmitter_country": "کویت",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "65°",
        "target_area": "خاورمیانه و آسیای میانه",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت رسمی HFCC B26",
        "notes": "ساعت ۰۶:۳۰ تا ۰۹:۳۰ صبح تهران؛ سیگنال بسیار قدرتمند از کویت."
    },
    {
        "station_id": "STN-VOA-EN",
        "program_title": "صدای آمریکا: سرویس انگلیسی عصرگاهی (باند ۱۹ متر)",
        "language": "en",
        "language_fa": "انگلیسی",
        "category": "news",
        "category_fa": "بین‌المللی و خبری",
        "frequency_khz": 15580,
        "modulation": "AM",
        "start_utc": "1400",
        "end_utc": "1700",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "نائن (آلمان)",
        "transmitter_site_code": "D-n",
        "transmitter_country": "آلمان",
        "transmitter_power_kw": 500,
        "azimuth_degrees": "115°",
        "target_area": "خاورمیانه",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: فرستنده ۵۰۰ کیلوواتی نائن",
        "notes": "ساعت ۱۷:۳۰ تا ۲۰:۳۰ شب تهران روی باند ۱۹ متر."
    },
    {
        "station_id": "STN-RRI",
        "program_title": "رادیو رومانی بین‌المللی: برنامه عصرگاهی به زبان انگلیسی",
        "language": "en",
        "language_fa": "انگلیسی",
        "category": "general",
        "category_fa": "فرهنگی و بین‌المللی",
        "frequency_khz": 9730,
        "modulation": "AM",
        "start_utc": "1700",
        "end_utc": "1800",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "گالوانی (رومانی)",
        "transmitter_site_code": "GAL",
        "transmitter_country": "رومانی",
        "transmitter_power_kw": 300,
        "azimuth_degrees": "110°",
        "target_area": "خاورمیانه و غرب آسیا",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: فرستنده ۳۰۰ کیلوواتی با پرتو مستقیم روی فلات ایران",
        "notes": "ساعت ۲۰:۳۰ تا ۲۱:۳۰ شب به وقت تهران. از بهترین ایستگاه‌های اروپایی برای دریافت در ایران."
    },
    {
        "station_id": "STN-RRI",
        "program_title": "رادیو رومانی بین‌المللی: بخش عربی ویژه خاورمیانه",
        "language": "ar",
        "language_fa": "عربی",
        "category": "general",
        "category_fa": "فرهنگی و بین‌المللی",
        "frequency_khz": 11850,
        "modulation": "AM",
        "start_utc": "1400",
        "end_utc": "1500",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "تیگَنِشتی (بخارست)",
        "transmitter_site_code": "TIG",
        "transmitter_country": "رومانی",
        "transmitter_power_kw": 300,
        "azimuth_degrees": "130°",
        "target_area": "خاورمیانه",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت HFCC B26",
        "notes": "ساعت ۱۷:۳۰ تا ۱۸:۳۰ عصر به وقت تهران."
    },
    {
        "station_id": "STN-REE",
        "program_title": "رادیو بین‌المللی اسپانیا (REE): برنامه به زبان اسپانیایی و انگلیسی",
        "language": "es",
        "language_fa": "اسپانیایی",
        "category": "general",
        "category_fa": "فرهنگی و خبری",
        "frequency_khz": 9690,
        "modulation": "AM",
        "start_utc": "1800",
        "end_utc": "2200",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "نوبله‌خاس (اسپانیا)",
        "transmitter_site_code": "NOB",
        "transmitter_country": "اسپانیا",
        "transmitter_power_kw": 350,
        "azimuth_degrees": "95°",
        "target_area": "اروپا، مدیترانه و خاورمیانه",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: فرستنده پرقدرت ۳۵۰ کیلووات نوبله‌خاس در مرکز اسپانیا",
        "notes": "ساعت ۲۱:۳۰ تا ۰۱:۳۰ بامداد روز بعد به وقت تهران. برنامه‌های فرهنگی و اخبار جهان اسپانیایی‌زبان."
    },
    {
        "station_id": "STN-RTI",
        "program_title": "رادیو تایوان بین‌المللی (RTI): برنامه خبری انگلیسی",
        "language": "en",
        "language_fa": "انگلیسی",
        "category": "general",
        "category_fa": "عمومی و خبری",
        "frequency_khz": 9545,
        "modulation": "AM",
        "start_utc": "1200",
        "end_utc": "1300",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "کوگا (تایوان)",
        "transmitter_site_code": "KOU",
        "transmitter_country": "تایوان",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "290°",
        "target_area": "جنوب و غرب آسیا",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت در جدول HFCC B26",
        "notes": "ساعت ۱۵:۳۰ تا ۱۶:۳۰ بعدازظهر به وقت تهران."
    },
    {
        "station_id": "STN-KBS",
        "program_title": "رادیو جهانی کی‌بی‌اس کره جنوبی: بخش انگلیسی (باند ۳۱ متر)",
        "language": "en",
        "language_fa": "انگلیسی",
        "category": "general",
        "category_fa": "عمومی، فرهنگی و کی‌پاپ",
        "frequency_khz": 9515,
        "modulation": "AM",
        "start_utc": "1400",
        "end_utc": "1500",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "کیمجه (کره جنوبی)",
        "transmitter_site_code": "KIM",
        "transmitter_country": "کره جنوبی",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "285°",
        "target_area": "غرب آسیا و خاورمیانه",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت HFCC B26",
        "notes": "ساعت ۱۷:۳۰ تا ۱۸:۳۰ عصر به وقت تهران؛ اخبار سئول، فناوری و موسیقی مدرن کره‌ای."
    },
    {
        "station_id": "STN-KBS",
        "program_title": "رادیو جهانی کی‌بی‌اس کره جنوبی: بخش عربی خاورمیانه",
        "language": "ar",
        "language_fa": "عربی",
        "category": "general",
        "category_fa": "عمومی و خبری",
        "frequency_khz": 9740,
        "modulation": "AM",
        "start_utc": "1600",
        "end_utc": "1700",
        "days": "1234567",
        "days_fa": "روزانه (هر روز)",
        "transmitter_site": "ووفِرتون (بریتانیا - رله)",
        "transmitter_site_code": "WO",
        "transmitter_country": "بریتانیا",
        "transmitter_power_kw": 250,
        "azimuth_degrees": "105°",
        "target_area": "خاورمیانه",
        "season": "B26 (زمستان ۲۰۲۶-۲۰۲۷)",
        "valid_from": "2026-10-25",
        "valid_to": "2027-03-27",
        "source_id": "SRC-HFCC-B26",
        "status": "verified_official",
        "status_fa": "تأییدشده رسمی",
        "confidence_level": "A",
        "confidence_description_fa": "سطح A: ثبت هماهنگی HFCC B26",
        "notes": "ساعت ۱۹:۳۰ تا ۲۰:۳۰ شب به وقت تهران."
    }
]

# ---------------------------------------------------------------------------
# LINK ALTERNATIVE FREQUENCIES AND NORMALIZE
# ---------------------------------------------------------------------------
def build_normalized_database():
    schedules = []
    
    # Pre-index schedules by station to find alternative frequencies
    station_freq_map = {}
    for item in RAW_SCHEDULES_DATA:
        stn = item['station_id']
        freq = item['frequency_khz']
        station_freq_map.setdefault(stn, set()).add(freq)
        
    station_lookup = {s['station_id']: s for s in STATIONS_DATA}
    source_lookup = {s['source_id']: s for s in SOURCES_DATA}
    
    for idx, raw in enumerate(RAW_SCHEDULES_DATA, start=1):
        sch_id = f"SCH-{idx:04d}"
        stn_id = raw['station_id']
        stn = station_lookup.get(stn_id, {})
        
        freq = raw['frequency_khz']
        band_info = classify_band(freq)
        time_info = process_time_span(raw['start_utc'], raw['end_utc'])
        
        # Get alternative frequencies for this station (excluding current freq)
        alt_freqs = sorted(list(station_freq_map.get(stn_id, set()) - {freq}))
        
        src_id = raw.get('source_id', 'SRC-HFCC-B26')
        src = source_lookup.get(src_id, {})
        
        # Format transmitter
        loc_code = raw.get('transmitter_site_code', 'XUU')
        
        rec = {
            "id": sch_id,
            "station_id": stn_id,
            "station_name_fa": stn.get('name_fa', 'نامشخص'),
            "station_name_en": stn.get('name_en', 'Unknown'),
            "program_title": raw['program_title'],
            "language": raw['language'],
            "language_fa": raw['language_fa'],
            "category": raw['category'],
            "category_fa": raw['category_fa'],
            "country": stn.get('country', 'INT'),
            "country_fa": stn.get('country_fa', 'بین‌المللی'),
            "broadcaster": stn.get('broadcaster', ''),
            "frequency_khz": freq,
            "frequency_display": f"{freq} kHz",
            "band_code": band_info['code'],
            "band_name_fa": band_info['name_fa'],
            "band_propagation_fa": band_info['prop_fa'],
            "modulation": raw['modulation'],
            "time_start_utc": f"{raw['start_utc'][:2]}:{raw['start_utc'][2:]}",
            "time_end_utc": f"{raw['end_utc'][:2]}:{raw['end_utc'][2:]}",
            "time_start_tehran": time_info['start_tehran'],
            "time_end_tehran": time_info['end_tehran'],
            "time_display_tehran": time_info['display_tehran'],
            "duration_minutes": time_info['duration_minutes'],
            "crosses_midnight_tehran": time_info['crosses_midnight'],
            "days_of_week": raw['days'],
            "days_of_week_fa": raw['days_fa'],
            "valid_from": raw['valid_from'],
            "valid_to": raw['valid_to'],
            "season": raw['season'],
            "transmitter_site": raw['transmitter_site'],
            "transmitter_site_code": loc_code,
            "transmitter_country": raw['transmitter_country'],
            "transmitter_power_kw": raw['transmitter_power_kw'],
            "azimuth_degrees": raw['azimuth_degrees'],
            "target_area": raw['target_area'],
            "source_id": src_id,
            "source_name": src.get('name_fa', 'کنفرانس بین‌المللی HFCC'),
            "source_url": src.get('url', 'http://www.hfcc.org/'),
            "collected_at": "2026-10-28T08:30:00+03:30",
            "status": raw['status'],
            "status_fa": raw['status_fa'],
            "confidence_level": raw['confidence_level'],
            "confidence_description_fa": raw['confidence_description_fa'],
            "alternative_frequencies": alt_freqs,
            "notes": raw['notes']
        }
        schedules.append(rec)
        
    return schedules

# ---------------------------------------------------------------------------
# WRITE CSV, JSON, TXT, EXCEL
# ---------------------------------------------------------------------------
def generate_all_outputs():
    schedules = build_normalized_database()
    
    # Calculate stats
    total_stations = len(STATIONS_DATA)
    total_schedules = len(schedules)
    farsi_schedules = [s for s in schedules if s['language'] in ['fa', 'dr', 'tj']]
    verified_schedules = [s for s in schedules if s['confidence_level'] in ['A', 'B']]
    review_schedules = [s for s in schedules if s['confidence_level'] in ['C', 'D']]
    
    metadata = {
        "project_name": "Iran SW Radio",
        "project_subtitle_fa": "راهنمای جامع، دقیق و آفلاین رادیوهای موج کوتاه برای ایران",
        "version": "2.0.0-B26",
        "season": "B26 (Winter 2026-2027) & A26",
        "created_at_tehran": "2026-10-28T08:30:12+03:30",
        "last_database_update": "2026-10-28",
        "timezone_reference": "Tehran (UTC+03:30 strict - Iran abolished DST in 2022)",
        "stats": {
            "total_stations": total_stations,
            "total_schedules": total_schedules,
            "total_farsi_schedules": len(farsi_schedules),
            "total_verified_schedules": len(verified_schedules),
            "total_needs_review": len(review_schedules),
            "total_sources": len(SOURCES_DATA)
        },
        "confidence_levels_definition": {
            "A": "تأییدشده رسمی: هماهنگ‌شده در سند بین‌المللی HFCC B26 و وبگاه رسمی اپراتور فرستنده",
            "B": "تأییدشده با چند منبع: لاگ‌های مانیتورینگ مستقل دایرکتوری EiBi و شنوندگان تخصصی DX",
            "C": "نیازمند بررسی / پخش اضطراری: رکوردهای رزرو یا پخش‌های مقطعی احزاب سیاسی و اپوزیسیون",
            "D": "اختلاف‌دار یا قدیمی: نیازمند ممیزی مجدد"
        }
    }
    
    database_json = {
        "metadata": metadata,
        "stations": STATIONS_DATA,
        "schedules": schedules,
        "sources": SOURCES_DATA
    }
    
    # 1. JSON
    json_path = os.path.join(DATA_DIR, 'radio-database.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(database_json, f, ensure_ascii=False, indent=2)
    print(f"Generated JSON: {json_path}")
    
    # 2. STATIONS CSV
    stations_csv_path = os.path.join(DATA_DIR, 'stations.csv')
    with open(stations_csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['station_id', 'name_fa', 'name_en', 'country', 'country_fa', 'broadcaster', 'category', 'category_fa', 'sw_status_fa', 'primary_transmitters_fa', 'confidence_level', 'website']
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for s in STATIONS_DATA:
            writer.writerow(s)
    print(f"Generated Stations CSV: {stations_csv_path}")

    # 3. SCHEDULES CSV
    schedules_csv_path = os.path.join(DATA_DIR, 'schedules.csv')
    with open(schedules_csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = [
            'id', 'station_id', 'station_name_fa', 'station_name_en', 'program_title',
            'language_fa', 'category_fa', 'frequency_khz', 'band_name_fa', 'modulation',
            'time_start_tehran', 'time_end_tehran', 'time_display_tehran', 'time_start_utc', 'time_end_utc',
            'days_of_week_fa', 'transmitter_site', 'transmitter_power_kw', 'azimuth_degrees', 'target_area',
            'season', 'status_fa', 'confidence_level', 'notes'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for s in schedules:
            writer.writerow(s)
    print(f"Generated Schedules CSV: {schedules_csv_path}")

    # 4. SOURCES CSV
    sources_csv_path = os.path.join(DATA_DIR, 'sources.csv')
    with open(sources_csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['source_id', 'name_fa', 'name_en', 'type_fa', 'url', 'collected_date', 'valid_period', 'description_fa']
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for s in SOURCES_DATA:
            writer.writerow(s)
    print(f"Generated Sources CSV: {sources_csv_path}")

    # 5. TXT EMERGENCY QUICK REFERENCE (SORTED BY TEHRAN TIME)
    txt_path = os.path.join(EXPORTS_DIR, 'Iran-SW-Radio-Emergency-Quick-Reference.txt')
    # Sort schedules primarily by Tehran start time, then frequency
    sorted_by_time = sorted(schedules, key=lambda x: (x['time_start_tehran'], x['frequency_khz']))
    
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("================================================================================\n")
        f.write("      IRAN SW RADIO - راهنمای اضطراری و آفلاین فرکانس‌های موج کوتاه ایران      \n")
        f.write("================================================================================\n")
        f.write(f"نسخه پایگاه داده: 2.0.0-B26 | تاریخ اعتبار: فصل زمستان B26 (۲۰۲۶-۲۰۲۷)\n")
        f.write(f"ساعت معیار: وقت رسمی تهران (UTC+03:30 بدون تغییر ساعت تابستانی)\n")
        f.write(f"تعداد کل رکوردهای فعال: {len(schedules)} | رکوردهای ویژه فارسی: {len(farsi_schedules)}\n")
        f.write("این راهنما در شرایط اضطراری، قطع کامل اینترنت و بدون برق شبکه قابل استفاده است.\n")
        f.write("--------------------------------------------------------------------------------\n\n")
        
        f.write("+++ بخش اول: جدول برنامه‌های فارسی‌زبان (مرتب‌شده بر اساس ساعت تهران) +++\n\n")
        f.write(f"{'ساعت تهران':<22} | {'فرکانس':<10} | {'باند':<14} | {'شبکه و برنامه':<30} | {'اعتبار':<6}\n")
        f.write("-" * 90 + "\n")
        for s in [x for x in sorted_by_time if x['language'] in ['fa', 'dr', 'tj']]:
            time_str = s['time_display_tehran']
            freq_str = f"{s['frequency_khz']} kHz"
            band_str = s['band_name_fa'].split('(')[0].strip()
            title_str = f"{s['station_name_fa']}"
            conf = f"سطح {s['confidence_level']}"
            f.write(f"{time_str:<22} | {freq_str:<10} | {band_str:<14} | {title_str:<30} | {conf:<6}\n")
            f.write(f"   ↳ {s['program_title']} [{s['transmitter_site']}]\n")

        f.write("\n" + "=" * 90 + "\n\n")
        f.write("+++ بخش دوم: جدول کل ایستگاه‌ها (فارسی و بین‌المللی) به ترتیب ساعت تهران +++\n\n")
        for s in sorted_by_time:
            f.write(f"[{s['time_display_tehran']}]  {s['frequency_khz']:>5} kHz ({s['band_name_fa']}) - {s['station_name_fa']} [{s['language_fa']}]\n")
            f.write(f"     فرستنده: {s['transmitter_site']} ({s['transmitter_power_kw'] or '?'} kW) | وضعیت: {s['status_fa']}\n")
            if s['alternative_frequencies']:
                alts = ", ".join([f"{a} kHz" for a in s['alternative_frequencies']])
                f.write(f"     فرکانس‌های جایگزین: {alts}\n")
            f.write("\n")

        f.write("================================================================================\n")
        f.write("راهنمای سریع تنظیم گیرنده رادیو:\n")
        f.write("۱. بیشتر رادیوهای موج کوتاه از مدولاسیون استاندارد AM استفاده می‌کنند.\n")
        f.write("۲. بهترین زمان دریافت باندهای ۴۹ متر (۶ مگاهرتز) و ۴۱ متر (۷ مگاهرتز) ساعات شب است.\n")
        f.write("۳. باندهای ۱۹ متر (۱۵ مگاهرتز) و ۲۵ متر (۱۲ مگاهرتز) در طول روز بسیار شفاف هستند.\n")
        f.write("۴. برای کاهش نویز، از آداپتورهای بی‌کیفیت موبایل، لامپ‌های LED و مودم فاصله بگیرید.\n")
        f.write("۵. اتصال یک سیم نازک ۲ تا ۵ متری به آنتن تلسکوپی گیرنده، قدرت دریافت را چند برابر می‌کند.\n")
        f.write("================================================================================\n")
    print(f"Generated TXT Quick Reference: {txt_path}")

    # 6. TXT FREQUENCY GUIDE (SORTED BY KHZ)
    freq_txt_path = os.path.join(EXPORTS_DIR, 'Iran-SW-Radio-Frequency-Guide.txt')
    sorted_by_freq = sorted(schedules, key=lambda x: (x['frequency_khz'], x['time_start_tehran']))
    with open(freq_txt_path, 'w', encoding='utf-8') as f:
        f.write("================================================================================\n")
        f.write("      IRAN SW RADIO - مرور تخصصی طیف فرکانسی موج کوتاه (کیلوهرتز kHz)         \n")
        f.write("================================================================================\n\n")
        for s in sorted_by_freq:
            f.write(f"{s['frequency_khz']:>6} kHz | {s['band_name_fa']:<24} | {s['time_display_tehran']:<20} | {s['station_name_fa']:<25} | {s['language_fa']}\n")
            f.write(f"       ↳ {s['program_title']} | فرستنده: {s['transmitter_site']} | سطح اطمینان: {s['confidence_level']}\n")
    print(f"Generated Frequency TXT Guide: {freq_txt_path}")

    # 7. MULTI-SHEET EXCEL (XLSX) WITH BEAUTIFUL PROFESSIONAL STYLING
    generate_excel_workbook(database_json, schedules)

def generate_excel_workbook(db_json, schedules):
    xlsx_path = os.path.join(EXPORTS_DIR, 'Iran-SW-Radio-Database.xlsx')
    wb = openpyxl.Workbook()
    
    # Styles
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    header_font = Font(name="Tahoma", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Tahoma", size=10)
    bold_font = Font(name="Tahoma", size=10, bold=True)
    border_thin = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    center_align = Alignment(horizontal="center", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")
    
    # Sheet 1: Schedules (جدول پخش)
    ws1 = wb.active
    ws1.title = "جدول پخش (Schedules)"
    ws1.views.sheetView[0].rightToLeft = True
    
    headers1 = [
        "شناسه", "نام شبکه (فارسی)", "نام شبکه (انگلیسی)", "عنوان برنامه",
        "زبان", "دسته‌بندی", "فرکانس (kHz)", "باند امواج", "مدولاسیون",
        "ساعت شروع (تهران)", "ساعت پایان (تهران)", "بازه پخش (تهران)",
        "ساعت شروع (UTC)", "ساعت پایان (UTC)", "روزهای پخش", "ایستگاه فرستنده",
        "توان (kW)", "جهت تابش", "منطقه هدف", "وضعیت اعتبار", "سطح اطمینان", "فرکانس‌های جایگزین", "توضیحات فنی"
    ]
    ws1.append(headers1)
    
    for s in schedules:
        alts_str = ", ".join([str(x) for x in s['alternative_frequencies']]) if s['alternative_frequencies'] else "ندارد"
        row = [
            s['id'], s['station_name_fa'], s['station_name_en'], s['program_title'],
            s['language_fa'], s['category_fa'], s['frequency_khz'], s['band_name_fa'], s['modulation'],
            s['time_start_tehran'], s['time_end_tehran'], s['time_display_tehran'],
            s['time_start_utc'], s['time_end_utc'], s['days_of_week_fa'], s['transmitter_site'],
            s['transmitter_power_kw'] or "", s['azimuth_degrees'], s['target_area'], s['status_fa'],
            s['confidence_level'], alts_str, s['notes']
        ]
        ws1.append(row)

    # Sheet 2: Stations (ایستگاه‌ها)
    ws2 = wb.create_sheet(title="ایستگاه‌ها (Stations)")
    ws2.views.sheetView[0].rightToLeft = True
    headers2 = [
        "شناسه ایستگاه", "نام رسمی (فارسی)", "نام لاتین", "کشور مبدا", "سازمان اداره‌کننده",
        "زبان‌های پخش", "دسته‌بندی اصلی", "وضعیت موج کوتاه", "فرستنده‌های اصلی", "سطح اطمینان", "وبگاه رسمی", "شرح فعالیت"
    ]
    ws2.append(headers2)
    for stn in STATIONS_DATA:
        langs_str = ", ".join(stn['languages_fa'])
        row = [
            stn['station_id'], stn['name_fa'], stn['name_en'], stn['country_fa'], stn['broadcaster'],
            langs_str, stn['category_fa'], stn['sw_status_fa'], stn['primary_transmitters_fa'],
            stn['confidence_level'], stn['website'] or "ندارد", stn['description_fa']
        ]
        ws2.append(row)

    # Sheet 3: Sources (منابع و مراجع)
    ws3 = wb.create_sheet(title="منابع (Sources)")
    ws3.views.sheetView[0].rightToLeft = True
    headers3 = ["شناسه منبع", "عنوان منبع (فارسی)", "عنوان انگلیسی", "نوع مرجع", "آدرس اینترنتی", "تاریخ گردآوری", "دوره اعتبار", "توضیحات و مستندات"]
    ws3.append(headers3)
    for src in SOURCES_DATA:
        row = [
            src['source_id'], src['name_fa'], src['name_en'], src['type_fa'],
            src['url'], src['collected_date'], src['valid_period'], src['description_fa']
        ]
        ws3.append(row)

    # Sheet 4: Needs Review (نیازمند بررسی)
    ws4 = wb.create_sheet(title="نیازمند بررسی (Needs Review)")
    ws4.views.sheetView[0].rightToLeft = True
    headers4 = ["شناسه", "نام شبکه", "فرکانس (kHz)", "ساعت تهران", "دلیل قرارگیری در این فهرست", "وضعیت فنی و اقدام پیشنهادی"]
    ws4.append(headers4)
    review_items = [s for s in schedules if s['confidence_level'] in ['C', 'D'] or 'emergency' in s['status']]
    for r in review_items:
        row = [
            r['id'], r['station_name_fa'], r['frequency_khz'], r['time_display_tehran'],
            r['status_fa'], r['confidence_description_fa'] + " | " + r['notes']
        ]
        ws4.append(row)

    # Sheet 5: Data Dictionary & Guide (راهنمای فیلدها)
    ws5 = wb.create_sheet(title="راهنما و تعاریف (Guide)")
    ws5.views.sheetView[0].rightToLeft = True
    headers5 = ["عنوان مفهوم / فیلد", "شرح و کاربرد فنی در پروژه رادیو موج کوتاه"]
    ws5.append(headers5)
    glossary = [
        ("ساعت تهران (Tehran Time)", "مبنای زمانی کل پروژه UTC+03:30 ثابت است؛ از سال ۲۰۲۲ تغییر ساعت فصلی در ایران لغو شده است."),
        ("فرکانس کیلوهرتز (kHz)", "واحد شمارش فرکانس‌های رادیویی موج کوتاه. تقسیم بر ۱۰۰۰ معادل مگاهرتز (MHz) است."),
        ("سطح اطمینان A (Confidence A)", "تأییدشده رسمی: تطبیق کامل بین هماهنگی بین‌المللی HFCC B26 و وبگاه رسمی سازمان پخش‌کننده."),
        ("سطح اطمینان B (Confidence B)", "تأییدشده با چند منبع: رصدهای میدانی مستقل شنوندگان و لاگ‌های دایرکتوری معتبر EiBi."),
        ("سطح اطمینان C (Confidence C)", "پخش اضطراری یا زیرزمینی: برنامه‌های احزاب سیاسی یا فرکانس‌های رزرو بحران که نیازمند راستی‌آزمایی در زمان شنود هستند."),
        ("باند ۴۹ متر (۵۸۰۰ تا ۶۲۰۰ کیلوهرتز)", "قوی‌ترین باند شبانگاهی در ایران؛ مناسب برای ساعات ۲۱:۰۰ تا ۰۶:۰۰ صبح."),
        ("باند ۳۱ متر (۹۴۰۰ تا ۹۹۰۰ کیلوهرتز)", "پایدارترین باند شبانه‌روزی با نفوذ عالی در تمام ساعات شب و عصر."),
        ("باند ۱۹ متر (۱۵۱۰۰ تا ۱۵۸۰۰ کیلوهرتز)", "بهترین باند روزانه برای دریافت فرستنده‌های بسیار دوردست در قاره‌های آسیا و اروپا.")
    ]
    for item in glossary:
        ws5.append([item[0], item[1]])

    # Format all sheets
    for ws in [ws1, ws2, ws3, ws4, ws5]:
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.font = data_font
                cell.border = border_thin
                if isinstance(cell.value, (int, float)):
                    cell.alignment = center_align
                else:
                    cell.alignment = right_align
        # Auto-adjust column widths
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                # approximate visual length for Persian chars
                cur_len = len(val_str)
                if cur_len > max_len:
                    max_len = cur_len
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

    wb.save(xlsx_path)
    print(f"Generated Multi-Sheet Excel: {xlsx_path}")

if __name__ == "__main__":
    generate_all_outputs()
