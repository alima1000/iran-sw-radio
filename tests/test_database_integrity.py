import unittest
import json
import os

class TestDatabaseIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_dir, 'data', 'radio-database.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            cls.db = json.load(f)
        cls.stations = {s['station_id']: s for s in cls.db['stations']}
        cls.schedules = cls.db['schedules']
        cls.sources = {s['source_id']: s for s in cls.db['sources']}

    def test_database_structure(self):
        self.assertIn('metadata', self.db)
        self.assertIn('stations', self.db)
        self.assertIn('schedules', self.db)
        self.assertIn('sources', self.db)
        self.assertGreater(len(self.stations), 15)
        self.assertGreater(len(self.schedules), 30)

    def test_frequency_ranges(self):
        for s in self.schedules:
            freq = s['frequency_khz']
            self.assertIsInstance(freq, (int, float))
            self.assertGreaterEqual(freq, 500, f"Frequency too low: {freq} for {s['id']}")
            self.assertLessEqual(freq, 30000, f"Frequency too high: {freq} for {s['id']}")

    def test_station_references(self):
        for s in self.schedules:
            stn_id = s['station_id']
            self.assertIn(stn_id, self.stations, f"Schedule {s['id']} references missing station {stn_id}")

    def test_source_references(self):
        for s in self.schedules:
            src_id = s['source_id']
            self.assertIn(src_id, self.sources, f"Schedule {s['id']} references missing source {src_id}")

    def test_confidence_and_status(self):
        valid_confidences = {'A', 'B', 'C', 'D'}
        valid_statuses = {'verified_official', 'verified_multi_source', 'single_source_reported', 'needs_review', 'historical_inactive', 'emergency_relay'}
        for s in self.schedules:
            self.assertIn(s['confidence_level'], valid_confidences)
            self.assertIn(s['status'], valid_statuses)

    def test_tehran_times_present(self):
        for s in self.schedules:
            self.assertTrue(s['time_start_tehran'], f"Missing start tehran time in {s['id']}")
            self.assertTrue(s['time_end_tehran'], f"Missing end tehran time in {s['id']}")
            self.assertIn(':', s['time_start_tehran'])
            self.assertIn(':', s['time_end_tehran'])

    def test_farsi_priority(self):
        farsi_count = sum(1 for s in self.schedules if s['language'] in ['fa', 'dr', 'tj'])
        self.assertGreater(farsi_count, len(self.schedules) * 0.5, "Persian broadcasts must form the majority of the active catalog")

if __name__ == '__main__':
    unittest.main()
