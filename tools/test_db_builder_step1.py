import os
import json
import csv
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# Ensure directories exist
os.makedirs('data', exist_ok=True)
os.makedirs('exports', exist_ok=True)
os.makedirs('raw_sources', exist_ok=True)

# ---------------------------------------------------------------------------
# 1. TIME CONVERSION LOGIC (TEHRAN UTC+03:30 STRICT)
# ---------------------------------------------------------------------------
def utc_to_tehran_time(utc_time_str):
    utc_clean = utc_time_str.replace(':', '').strip()
    if len(utc_clean) == 3:
        utc_clean = '0' + utc_clean
    if len(utc_clean) != 4 or not utc_clean.isdigit():
        return utc_time_str, 0
    h = int(utc_clean[:2])
    m = int(utc_clean[2:])
    tot_mins = h * 60 + m + 210  # +3h 30m
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

# ---------------------------------------------------------------------------
# 2. BAND AND PROPAGATION CLASSIFICATION
# ---------------------------------------------------------------------------
def classify_band(freq_khz):
    f = float(freq_khz)
    if 520 <= f <= 1710:
        return {'code': 'MW', 'name_fa': 'موج متوسط (MW)', 'name_en': 'Medium Wave', 'prop_fa': 'دریافت عالی در شب و پایدار تا فاصله‌های منطقه‌ای'}
    elif 2300 <= f <= 2500:
        return {'code': '120m', 'name_fa': 'باند ۱۲۰ متر', 'name_en': '120m Band', 'prop_fa': 'مخصوص شب؛ تضعیف شدید در روز'}
    elif 3200 <= f <= 3450:
        return {'code': '90m', 'name_fa': 'باند ۹۰ متر', 'name_en': '90m Band', 'prop_fa': 'باند شبانگاهی؛ دریافت فواصل نزدیک و منطقه‌ای'}
    elif 3900 <= f <= 4050:
        return {'code': '75m', 'name_fa': 'باند ۷۵ متر', 'name_en': '75m Band', 'prop_fa': 'شبانگاهی در فصول سرد سال'}
    elif 4750 <= f <= 5100:
        return {'code': '60m', 'name_fa': 'باند ۶۰ متر', 'name_en': '60m Band', 'prop_fa': 'پایان بعدازظهر تا سحرگاه'}
    elif 5800 <= f <= 6300:
        return {'code': '49m', 'name_fa': 'باند ۴۹ متر', 'name_en': '49m Band', 'prop_fa': 'قدرتمندترین باند شبانگاهی موج کوتاه در ایران؛ عبور راحت از موانع'}
    elif 7200 <= f <= 7600:
        return {'code': '41m', 'name_fa': 'باند ۴۱ متر', 'name_en': '41m Band', 'prop_fa': 'باند بسیار کلیدی در ساعات غروب، شب و اوایل صبح'}
    elif 9300 <= f <= 10000:
        return {'code': '31m', 'name_fa': 'باند ۳۱ متر', 'name_en': '31m Band', 'prop_fa': 'محبوب‌ترین و پایدارترین باند شبانه‌روزی برای ارتباطات بین‌المللی'}
    elif 11500 <= f <= 12200:
        return {'code': '25m', 'name_fa': 'باند ۲۵ متر', 'name_en': '25m Band', 'prop_fa': 'دریافت خوب در ساعات بعدازظهر، غروب و تابستان‌ها در طول شب'}
    elif 13500 <= f <= 13900:
        return {'code': '22m', 'name_fa': 'باند ۲۲ متر', 'name_en': '22m Band', 'prop_fa': 'باند ویژه روزانه برای مسافت‌های بسیار دور'}
    elif 15000 <= f <= 15900:
        return {'code': '19m', 'name_fa': 'باند ۱۹ متر', 'name_en': '19m Band', 'prop_fa': 'بهترین باند روزانه در تمام فصول سال؛ دریافت شفاف از آسیا و اروپا'}
    elif 17400 <= f <= 18100:
        return {'code': '16m', 'name_fa': 'باند ۱۶ متر', 'name_en': '16m Band', 'prop_fa': 'روزانه در اوج تابش خورشید؛ حساس به فعالیت لکههای خورشیدی'}
    elif 21400 <= f <= 21850:
        return {'code': '13m', 'name_fa': 'باند ۱۳ متر', 'name_en': '13m Band', 'prop_fa': 'روزانه در شرایط انتشار عالی'}
    else:
        return {'code': 'OTHER', 'name_fa': 'باند متفرقه SW', 'name_en': 'SW Out of Band', 'prop_fa': 'باند فرعی یا ارتباطات اختصاصی'}

# ---------------------------------------------------------------------------
# 3. KNOWN TRANSMITTER DICTIONARY
# ---------------------------------------------------------------------------
TRANSMITTERS = {
    'KWT': {'name_fa': 'الکبد (کویت)', 'name_en': 'Kabd, Kuwait', 'country_fa': 'کویت', 'country_en': 'Kuwait', 'coords': '29.17° N, 47.78° E', 'default_pwr': 250},
    'DHA': {'name_fa': 'الضبایه (امارات)', 'name_en': 'Al Dhabbaya, UAE', 'country_fa': 'امارات متحده عربی', 'country_en': 'UAE', 'coords': '24.16° N, 53.79° E', 'default_pwr': 250},
    'EMR': {'name_fa': 'امیرلر (ترکیه)', 'name_en': 'Emirler, Turkey', 'country_fa': 'ترکیه', 'country_en': 'Turkey', 'coords': '39.58° N, 32.86° E', 'default_pwr': 500},
    'XIA': {'name_fa': 'شی‌آن (چین)', 'name_en': 'Xian, China', 'country_fa': 'چین', 'country_en': 'China', 'coords': '34.26° N, 108.94° E', 'default_pwr': 500},
    'BEI': {'name_fa': 'پکن (چین)', 'name_en': 'Beijing, China', 'country_fa': 'چین', 'country_en': 'China', 'coords': '39.90° N, 116.40° E', 'default_pwr': 500},
    'KAS': {'name_fa': 'کاشغر (چین)', 'name_en': 'Kashgar, China', 'country_fa': 'چین', 'country_en': 'China', 'coords': '39.47° N, 75.99° E', 'default_pwr': 500},
    'UR':  {'name_fa': 'ارومچی (چین)', 'name_en': 'Urumqi, China', 'country_fa': 'چین', 'country_en': 'China', 'coords': '43.82° N, 87.61° E', 'default_pwr': 500},
    'BG':  {'name_fa': 'بنگالورو (هند)', 'name_en': 'Bengaluru, India', 'country_fa': 'هند', 'country_en': 'India', 'coords': '12.97° N, 77.59° E', 'default_pwr': 250},
    'DE':  {'name_fa': 'دهلی (هند)', 'name_en': 'Delhi, India', 'country_fa': 'هند', 'country_en': 'India', 'coords': '28.61° N, 77.20° E', 'default_pwr': 100},
    'YA':  {'name_fa': 'یاماتا (ژاپن)', 'name_en': 'Yamata, Japan', 'country_fa': 'ژاپن', 'country_en': 'Japan', 'coords': '36.17° N, 139.83° E', 'default_pwr': 300},
    'BUL': {'name_fa': 'کوستینبرود (بلغارستان - اسپیس‌لاین)', 'name_en': 'Kostinbrod, Bulgaria', 'country_fa': 'بلغارستان', 'country_en': 'Bulgaria', 'coords': '42.82° N, 23.18° E', 'default_pwr': 100},
    'ARM': {'name_fa': 'گاوار (ارمنستان)', 'name_en': 'Gavar, Armenia', 'country_fa': 'ارمنستان', 'country_en': 'Armenia', 'coords': '40.36° N, 45.13° E', 'default_pwr': 500},
    'CYP': {'name_fa': 'زیگی (قبرس)', 'name_en': 'Zygi, Cyprus', 'country_fa': 'قبرس', 'country_en': 'Cyprus', 'coords': '34.72° N, 33.32° E', 'default_pwr': 300},
    'OMA': {'name_fa': 'الاشخره (عمان)', 'name_en': 'Al Ashkharah, Oman', 'country_fa': 'عمان', 'country_en': 'Oman', 'coords': '21.84° N, 59.58° E', 'default_pwr': 800},
    'TJK': {'name_fa': 'اورزو / دوشنبه (تاجیکستان)', 'name_en': 'Orzu, Tajikistan', 'country_fa': 'تاجیکستان', 'country_en': 'Tajikistan', 'coords': '37.55° N, 68.72° E', 'default_pwr': 1000},
    'UZB': {'name_fa': 'تاشکند (ازبکستان)', 'name_en': 'Tashkent, Uzbekistan', 'country_fa': 'ازبکستان', 'country_en': 'Uzbekistan', 'coords': '41.31° N, 69.24° E', 'default_pwr': 100},
    'D-n': {'name_fa': 'نائن (آلمان)', 'name_en': 'Nauen, Germany', 'country_fa': 'آلمان', 'country_en': 'Germany', 'coords': '52.64° N, 12.90° E', 'default_pwr': 500},
    'D-bb':{'name_fa': 'بیبلیس (آلمان)', 'name_en': 'Biblis, Germany', 'country_fa': 'آلمان', 'country_en': 'Germany', 'coords': '49.68° N, 8.41° E', 'default_pwr': 100},
    'WO':  {'name_fa': 'ووفِرتون (بریتانیا)', 'name_en': 'Woofferton, UK', 'country_fa': 'بریتانیا', 'country_en': 'UK', 'coords': '52.31° N, 2.71° W', 'default_pwr': 250},
    'IRN-K':{'name_fa': 'کمال‌آباد کرج (ایران)', 'name_en': 'Kamalabad, Iran', 'country_fa': 'ایران', 'country_en': 'Iran', 'coords': '35.80° N, 50.88° E', 'default_pwr': 500},
    'IRN-S':{'name_fa': 'سیرجان (ایران)', 'name_en': 'Sirjan, Iran', 'country_fa': 'ایران', 'country_en': 'Iran', 'coords': '29.45° N, 55.68° E', 'default_pwr': 500},
    'IRN-Z':{'name_fa': 'زاهدان (ایران)', 'name_en': 'Zahedan, Iran', 'country_fa': 'ایران', 'country_en': 'Iran', 'coords': '29.49° N, 60.86° E', 'default_pwr': 500},
    'GAL': {'name_fa': 'گالوانی (رومانی)', 'name_en': 'Galbeni, Romania', 'country_fa': 'رومانی', 'country_en': 'Romania', 'coords': '46.75° N, 26.86° E', 'default_pwr': 300},
    'TIG': {'name_fa': 'تیگَنِشتی (رومانی)', 'name_en': 'Tiganesti, Romania', 'country_fa': 'رومانی', 'country_en': 'Romania', 'coords': '44.70° N, 26.10° E', 'default_pwr': 300},
    'NOB': {'name_fa': 'نوبله‌خاس (اسپانیا)', 'name_en': 'Noblejas, Spain', 'country_fa': 'اسپانیا', 'country_en': 'Spain', 'coords': '39.96° N, 3.44° W', 'default_pwr': 350},
    'KIM': {'name_fa': 'کیمجه (کره جنوبی)', 'name_en': 'Gimje, South Korea', 'country_fa': 'کره جنوبی', 'country_en': 'South Korea', 'coords': '35.79° N, 126.83° E', 'default_pwr': 250},
    'KOU': {'name_fa': 'کوگا (تایوان)', 'name_en': 'Kouhu, Taiwan', 'country_fa': 'تایوان', 'country_en': 'Taiwan', 'coords': '23.58° N, 120.18° E', 'default_pwr': 250},
    'XUU': {'name_fa': 'نامشخص / ایستگاه زیرزمینی یا فرستنده متغیر', 'name_en': 'Clandestine / Variable Relay', 'country_fa': 'بین‌المللی', 'country_en': 'International', 'coords': None, 'default_pwr': None}
}

# ---------------------------------------------------------------------------
# 4. LOAD HFCC AND EIBI DATA
# ---------------------------------------------------------------------------
def load_hfcc_records():
    path_b26 = os.path.join('raw_sources', 'hfcc_b26', 'B26all00.TXT')
    if not os.path.exists(path_b26):
        return []
    with open(path_b26, 'r', encoding='latin1') as f:
        lines = [l.strip('\r\n') for l in f if not l.startswith(';') and len(l) > 50]
    
    records = []
    for line in lines:
        try:
            freq = line[0:5].strip()
            strt = line[5:9].strip()
            stop = line[10:14].strip()
            ciraf = line[15:45].strip()
            loc = line[46:49].strip()
            pwr = line[50:54].strip()
            azim = line[55:62].strip()
            ant = line[67:71].strip()
            days = line[71:78].strip()
            fdate = line[79:85].strip()
            tdate = line[86:92].strip()
            mod = line[93:94].strip()
            afrq = line[95:101].strip()
            lang = line[101:112].strip()
            adm = line[112:116].strip()
            brc = line[116:120].strip()
            fmo = line[120:124].strip()
            
            records.append({
                'freq': float(freq),
                'strt_utc': strt,
                'stop_utc': stop,
                'ciraf': ciraf,
                'loc': loc,
                'pwr': float(pwr) if pwr.isdigit() else None,
                'azim': azim,
                'days': days,
                'fdate': fdate,
                'tdate': tdate,
                'mod': mod if mod else 'AM',
                'lang': lang,
                'adm': adm,
                'brc': brc,
                'fmo': fmo
            })
        except Exception as e:
            continue
    return records

print(f"Loaded HFCC records successfully.")
