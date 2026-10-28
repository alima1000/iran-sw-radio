import requests
from html.parser import HTMLParser

for s in ['a26', 'b26']:
    url = f"http://www.hfcc.org/data/{s}/"
    r = requests.get(url, timeout=10)
    print(f"HFCC {s} status:", r.status_code)
    class P(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links = []
        def handle_starttag(self, tag, attrs):
            if tag == "a":
                for k, v in attrs:
                    if k == "href": self.links.append(v)
    p = P()
    p.feed(r.text)
    for l in p.links:
        if any(ext in l.lower() for ext in ['.txt', '.zip', '.csv']):
            print(f"  {s}:", l)
