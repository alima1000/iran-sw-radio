import requests
from html.parser import HTMLParser
import re

url = "http://www.eibispace.de/"
r = requests.get(url, timeout=15)
print("EiBi main page status:", r.status_code)

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for k, v in attrs:
                if k == "href":
                    self.links.append(v)

parser = LinkParser()
parser.feed(r.text)

print("Found links:")
for l in parser.links:
    if any(ext in l.lower() for ext in ['.txt', '.csv', 'bc-', 'freq-', '.zip', '.htm', 'a2', 'b2']):
        print(" -", l)
