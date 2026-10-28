import requests
import zipfile
import io
import os

os.makedirs('raw_sources', exist_ok=True)

# 1. Download EiBi files
eibi_files = {
    'sked-a26.csv': 'http://www.eibispace.de/dx/sked-a26.csv',
    'bc-a26.txt': 'http://www.eibispace.de/dx/bc-a26.txt',
    'freq-a26.txt': 'http://www.eibispace.de/dx/freq-a26.txt',
    'README.TXT': 'http://www.eibispace.de/dx/README.TXT'
}

for name, url in eibi_files.items():
    dest = os.path.join('raw_sources', f'eibi_{name}')
    if not os.path.exists(dest):
        print(f"Downloading EiBi: {name}...")
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            with open(dest, 'wb') as f:
                f.write(r.content)
            print(f"Saved {dest} ({len(r.content)} bytes)")
        else:
            print(f"Failed {name}: status {r.status_code}")

# 2. Download HFCC files
hfcc_zips = {
    'a26': 'http://www.hfcc.org/data/a26/a26allx2.zip',
    'b26': 'http://www.hfcc.org/data/b26/b26allx2.zip'
}

for season, url in hfcc_zips.items():
    dest_zip = os.path.join('raw_sources', f'hfcc_{season}.zip')
    extract_dir = os.path.join('raw_sources', f'hfcc_{season}')
    os.makedirs(extract_dir, exist_ok=True)
    if not os.path.exists(dest_zip):
        print(f"Downloading HFCC {season}...")
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            with open(dest_zip, 'wb') as f:
                f.write(r.content)
            print(f"Saved {dest_zip} ({len(r.content)} bytes)")
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                z.extractall(extract_dir)
                print(f"Extracted {season} to {extract_dir}: {z.namelist()[:5]}")
        else:
            print(f"Failed HFCC {season}: status {r.status_code}")
