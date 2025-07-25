import unittest
from src.correlate import group_events

class TestGroupEvents(unittest.TestCase):
    def test_group_by_combined_similarity(self):
        events = [
            {
                "title": "disk space low on host1",
                "text": "host1 /var disk at 90%",
                "tags": ["host:host1", "service:disk"],
            },
            {
                "title": "disk space low on host2",
                "text": "host2 /var disk at 92%",
                "tags": ["host:host2", "service:disk"],
            },
            {
                "title": "cpu usage high",
                "text": "host1 cpu at 90%",
                "tags": ["host:host1", "service:cpu"],
            },
            {
                "title": "disk space warning host1",
                "text": "disk at 85% on host1",
                "tags": ["host:host1", "service:disk"],
            },
        ]
        groups = group_events(events, similarity_threshold=0.5)
        self.assertEqual(len(groups), 2)
        lengths = sorted(len(g) for g in groups)
        self.assertEqual(lengths, [1, 3])

if __name__ == "__main__":
    unittest.main()
