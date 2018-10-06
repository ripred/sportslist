#!/usr/bin/env python3
""" unit tests for sports.py """

import unittest
import os
import json
import urllib.request
import sports

nhl_api_url = 'https://statsapi.web.nhl.com/api/v1/schedule'
mlb_api_url = 'https://statsapi.mlb.com/api/v1/schedule?sportId=1'


class SportsTests(unittest.TestCase):
    """Tests for the ``sports.py`` functions."""

    def setUp(self):
        """Fixture that loads the test data for the unit tests to use."""

        self.games_dict = {}
        self.all_games = {}

        basepath = os.getcwd()
        filename = basepath + '/test.json'
        with urllib.request.urlopen(''.join(['file://', filename])) as url:
            raw_data = url.read().decode('utf-8')
            self.json_data = json.loads(raw_data)

    def tearDown(self):
        """Fixture that removes the test data used by the unit tests."""
        del self.json_data

    def test_1_create_games_dict(self):
        self.all_games = self.json_data['dates'][0]['games']
        self.games_dict = sports.create_games_dict(self.all_games)
        self.assertEqual(sports.get_games_count(self.json_data), 8)

    def test_2_json_data_structure(self):
        # perform basic sanity checks on the game dictionary structure
        self.assertTrue(isinstance(self.json_data, dict))
        self.assertTrue('dates' in self.json_data)
        self.assertTrue(isinstance(self.json_data['dates'], list))
        self.assertGreater(len(self.json_data['dates']), 0)
        self.assertTrue(isinstance(self.json_data['dates'][0], dict))
        self.assertTrue('games' in self.json_data['dates'][0])

    def test_3_games_times_ascending(self):
        last_key = ''
        all_games = self.json_data['dates'][0]['games']
        self.games_dict = sports.create_games_dict(all_games)
        for key in self.games_dict:
            self.assertGreaterEqual(key[:5], last_key)
            last_key = key[:5]

    def test_4_function_runs(self):
        """Basic smoke test: Does the function run?"""
        print()
        sports.process_command_line(['sports.py', 'c', 't', 'h'])


if __name__ == '__main__':
    unittest.main()
