import os
import json
import csv
from datetime import datetime

# Mandatory UTC to Tehran conversion function
def utc_to_tehran_time(utc_time_str):
    """
    Converts 'HH:MM' or 'HHMM' from UTC to Tehran time (UTC+03:30).
    Tehran timezone is strictly UTC+03:30 (Iran abolished DST in 2022).
    Returns (tehran_time_str, day_offset)
    day_offset: 0 if same day, +1 if crosses midnight.
    """
    if '-' in utc_time_str:
        utc_time_str = utc_time_str.split('-')[0]
    utc_time_str = utc_time_str.replace(':', '').strip()
    if len(utc_time_str) == 3:
        utc_time_str = '0' + utc_time_str
    if len(utc_time_str) != 4 or not utc_time_str.isdigit():
        return utc_time_str, 0
    
    hours = int(utc_time_str[:2])
    minutes = int(utc_time_str[2:])
    
    # Add 3 hours and 30 minutes
    tot_minutes = hours * 60 + minutes + 210 # 3*60 + 30 = 210 mins
    
    day_offset = tot_minutes // 1440
    rem_minutes = tot_minutes % 1440
    
    th_hours = rem_minutes // 60
    th_minutes = rem_minutes % 60
    
    return f"{th_hours:02d}:{th_minutes:02d}", day_offset

def format_time_range_tehran(start_utc, end_utc):
    st_th, st_off = utc_to_tehran_time(start_utc)
    en_th, en_off = utc_to_tehran_time(end_utc)
    
    # Calculate duration in minutes
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
        desc = f"{st_th} تا {en_th} (۲۴ ساعته)"
    elif en_off > st_off or (end_total < start_total):
        desc = f"{st_th} تا {en_th} (روز بعد)"
        crosses_midnight = True
    else:
        desc = f"{st_th} تا {en_th}"
        
    return {
        'start_tehran': st_th,
        'end_tehran': en_th,
        'display_tehran': desc,
        'crosses_midnight': crosses_midnight,
        'duration_minutes': duration
    }

# Test mandatory test cases from prompt section 13:
print("--- Section 13 Mandatory Time Tests ---")
test_cases = [
    ('0000', '03:30', 0),
    ('0630', '10:00', 0),
    ('1630', '20:00', 0),
    ('2030', '00:00', 1), # next day midnight
    ('2200', '01:30', 1), # next day 01:30
]

for utc, expected_th, expected_off in test_cases:
    th, off = utc_to_tehran_time(utc)
    passed = (th == expected_th and off == expected_off)
    print(f"UTC {utc} -> Tehran {th} (offset +{off}) | Expected: {expected_th} (+{expected_off}) -> {'PASS' if passed else 'FAIL'}")
