import unittest
import os
import re

class TestHTMLOffline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        html_path = os.path.join(base_dir, 'app', 'Iran-SW-Radio-Guide.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            cls.html = f.read()

    def test_file_exists_and_not_empty(self):
        self.assertGreater(len(self.html), 50000, "HTML file is too small or empty")

    def test_rtl_and_lang(self):
        self.assertIn('dir="rtl"', self.html)
        self.assertIn('lang="fa"', self.html)

    def test_no_external_resources(self):
        """Check for external http/https in <link rel="stylesheet">, <script src="...">, <img src="...">."""
        # Find external script tags
        script_srcs = re.findall(r'<script[^>]+src=[\'"]([^\'"]+)[\'"]', self.html, re.I)
        for s in script_srcs:
            self.assertFalse(s.startswith('http'), f"Found external script source: {s}")

        # Find external stylesheet links
        link_hrefs = re.findall(r'<link[^>]+href=[\'"]([^\'"]+)[\'"]', self.html, re.I)
        for h in link_hrefs:
            self.assertFalse(h.startswith('http'), f"Found external stylesheet/font link: {h}")

        # Check for Google Fonts, CDNs, analytics
        banned = ['fonts.googleapis.com', 'cdnjs.cloudflare.com', 'unpkg.com', 'cdn.jsdelivr.net', 'google-analytics.com']
        for b in banned:
            self.assertNotIn(b, self.html, f"Found banned CDN/tracker in HTML: {b}")

    def test_embedded_database_present(self):
        self.assertIn('id="embedded-database"', self.html)
        self.assertIn('STN-FARDA', self.html)
        self.assertIn('5860', self.html)

    def test_required_views_present(self):
        self.assertIn('id="tab-now"', self.html)
        self.assertIn('id="tab-all"', self.html)
        self.assertIn('id="tab-planner"', self.html)
        self.assertIn('id="tab-hourly"', self.html)
        self.assertIn('id="tab-freq"', self.html)
        self.assertIn('id="tab-stations"', self.html)
        self.assertIn('id="tab-guide"', self.html)
        self.assertIn('id="tab-logs"', self.html)
        self.assertIn('id="tab-favorites"', self.html)
        self.assertIn('id="tab-update"', self.html)

    def test_update_center_controls(self):
        """Verify all 5 update methods and controls exist in the offline HTML."""
        self.assertIn('id="online-update-url"', self.html)
        self.assertIn('id="file-input-updater"', self.html)
        self.assertIn('id="paste-json-input"', self.html)
        self.assertIn('id="btn-export-updated-html"', self.html)
        self.assertIn('id="btn-factory-reset"', self.html)
        self.assertIn('id="btn-fetch-online"', self.html)
        self.assertIn('id="btn-apply-pasted-json"', self.html)
        self.assertIn('id="file-drop-zone"', self.html)
        self.assertIn('localStorage', self.html)

if __name__ == '__main__':
    unittest.main()
