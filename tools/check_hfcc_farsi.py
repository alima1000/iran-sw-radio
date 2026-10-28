import os

path_b26 = os.path.join('raw_sources', 'hfcc_b26', 'B26all00.TXT')
with open(path_b26, 'r', encoding='latin1') as f:
    lines = f.readlines()

print(f"Total entries in HFCC B26: {len(lines)}")
farsi_hfcc = []
for line in lines:
    if line.startswith(';') or len(line) < 50:
        continue
    # LANGUAGE is around columns 96-106 or let's inspect the split
    parts = line.split()
    # Let's search line for Per, Pes, Fas, Prs, Farda, IRIB, BBC
    lower = line.lower()
    if any(k in lower for k in ['per', 'pes', 'fas', 'prs', 'farda', 'irib', 'voa', 'cri', 'trt']):
        # check language specifically
        farsi_hfcc.append(line.strip())

print(f"Candidate lines in HFCC B26: {len(farsi_hfcc)}")
# Print first 20
for l in farsi_hfcc[:20]:
    print(l)
