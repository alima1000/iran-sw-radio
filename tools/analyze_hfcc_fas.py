import os
import re

def parse_hfcc_line(line):
    # Fixed format or regex
    # Columns in HFCC:
    # FREQ(0:4) STRT(5:9) STOP(10:14) CIRAF(15:45) LOC(46:49) POWR(50:54) AZIMUTH(55:62) SLW(63:66) ANT(67:70) DAYS(71:78) FDATE(79:85) TDATE(86:92) MOD(93:94) AFRQ(96:101) LANGUAGE(102:112) ADM(113:116) BRC(117:120) FMO(121:124)
    # Let's inspect line length and columns
    freq = line[0:4].strip()
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
    notes = line[124:].strip()
    return {
        'freq': freq, 'strt': strt, 'stop': stop, 'ciraf': ciraf, 'loc': loc,
        'pwr': pwr, 'azim': azim, 'ant': ant, 'days': days, 'fdate': fdate,
        'tdate': tdate, 'mod': mod, 'afrq': afrq, 'lang': lang, 'adm': adm,
        'brc': brc, 'fmo': fmo, 'notes': notes, 'raw': line
    }

path_b26 = os.path.join('raw_sources', 'hfcc_b26', 'B26all00.TXT')
with open(path_b26, 'r', encoding='latin1') as f:
    lines = [l.strip('\r\n') for l in f if not l.startswith(';') and len(l) > 50]

parsed = [parse_hfcc_line(l) for l in lines]
fas_records = [p for p in parsed if p['lang'] in ['Fas', 'Prs', 'Far', 'Per', 'Pes'] or '40' in p['ciraf'] and p['lang'] in ['Fas', 'Prs']]

print(f"HFCC B26: Total parsed = {len(parsed)}, Fas/Prs = {len(fas_records)}")
by_brc = {}
for p in fas_records:
    by_brc.setdefault((p['brc'], p['lang']), []).append(p)

for (brc, lang), recs in sorted(by_brc.items()):
    print(f"Broadcaster: {brc} | Lang: {lang} | Records: {len(recs)}")
    for r in recs[:4]:
        print(f"   {r['freq']} kHz | {r['strt']}-{r['stop']} UTC | CIRAF: {r['ciraf']} | LOC: {r['loc']} | PWR: {r['pwr']}kW | DAYS: {r['days']}")
