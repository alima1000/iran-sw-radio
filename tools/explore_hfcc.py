import requests
from html.parser import HTMLParser

url = "http://www.hfcc.org/data/"
r = requests.get(url, timeout=10)
print("HFCC status:", r.status_code)

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

print("Relevant links on HFCC:")
for l in parser.links:
    if any(x in l.lower() for x in ['a26', 'b25', 'a25', 'b24', '.zip', '.txt', 'sched']):
        print(" -", l)
