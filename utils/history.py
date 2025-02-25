
import json
from collections import defaultdict


class LocatorHistoryAnalyzer:
    def __init__(self, history_file):
        self.history_file = history_file

    def get_flaky_locators(self):
        with open(self.history_file) as f:
            data = json.load(f)

        stats = defaultdict(lambda: {'changes': 0, 'successes': 0})
        for entry in data:
            key = f"{entry['element']}-{entry['old_locator']['value']}"
            stats[key]['changes'] += 1
            if entry['success']:
                stats[key]['successes'] += 1

        return {
            element: stats
            for element, stats in stats.items()
            if stats['changes'] > 1
        }
