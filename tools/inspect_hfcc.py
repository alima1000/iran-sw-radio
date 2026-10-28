import os

# Check first 20 lines of HFCC B26all00.TXT
path = os.path.join('raw_sources', 'hfcc_b26', 'B26all00.TXT')
with open(path, 'r', encoding='latin1') as f:
    for i in range(25):
        print(f.readline().strip())
