import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from build_database import utc_to_tehran_time, process_time_span, classify_band

class TestTimeConversion(unittest.TestCase):
    def test_mandatory_prompt_cases(self):
        """Test the mandatory test cases from prompt section 13."""
        # 00:00 UTC == 03:30 Tehran
        th, off = utc_to_tehran_time('0000')
        self.assertEqual(th, '03:30')
        self.assertEqual(off, 0)

        # 06:30 UTC == 10:00 Tehran
        th, off = utc_to_tehran_time('0630')
        self.assertEqual(th, '10:00')
        self.assertEqual(off, 0)

        # 16:30 UTC == 20:00 Tehran
        th, off = utc_to_tehran_time('1630')
        self.assertEqual(th, '20:00')
        self.assertEqual(off, 0)

        # 20:30 UTC == 00:00 next day in Tehran
        th, off = utc_to_tehran_time('2030')
        self.assertEqual(th, '00:00')
        self.assertEqual(off, 1)

        # 22:00 UTC == 01:30 next day in Tehran
        th, off = utc_to_tehran_time('2200')
        self.assertEqual(th, '01:30')
        self.assertEqual(off, 1)

    def test_crossover_intervals(self):
        """Test interval crossing midnight."""
        # 19:00 UTC to 04:00 UTC (22:30 to 07:30 Tehran next day)
        res = process_time_span('1900', '0400')
        self.assertEqual(res['start_tehran'], '22:30')
        self.assertEqual(res['end_tehran'], '07:30')
        self.assertTrue(res['crosses_midnight'])
        self.assertEqual(res['duration_minutes'], 540) # 9 hours
        self.assertIn('روز بعد', res['display_tehran'])

    def test_24h_broadcast(self):
        res = process_time_span('0000', '2400')
        self.assertEqual(res['duration_minutes'], 1440)
        self.assertIn('۲۴ ساعته', res['display_tehran'])

    def test_band_classification(self):
        self.assertEqual(classify_band(5860)['code'], '49m')
        self.assertEqual(classify_band(7415)['code'], '41m')
        self.assertEqual(classify_band(9360)['code'], '31m')
        self.assertEqual(classify_band(12005)['code'], '25m')
        self.assertEqual(classify_band(13600)['code'], '22m')
        self.assertEqual(classify_band(15720)['code'], '19m')
        self.assertEqual(classify_band(864)['code'], 'MW')

if __name__ == '__main__':
    unittest.main()
