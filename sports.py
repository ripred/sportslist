#!/usr/bin/env python3
# sports.py

"""
A python script to retrieve and print
the day's hockey and/or baseball games
"""

# 2018 - ++tmw

import sys
import ssl
import urllib
import urllib.request
import json
from datetime import datetime
import time

# Set up lists of favorite teams and rival teams for both hockey and baseball
FAVORITES = [
    'Dallas Stars',
    'Pittsburgh Penguins',
    'Detroit Red Wings',
    'Arizona Coyotes',
    'Calgary Flames',
    'Texas Rangers',
    'Houston Astros']

RIVALS = [
    'Nashville Predators',
    'Winnipeg Jets',
    'Minnesota Wild',
    'Colorado Avalanche',
    'St Louis Blues',
    'Chicago Blackhawks',
    'Los Angeles Angels',
    'Houston Astros',
    'Seattle Mariners',
    'Oakland Athletics']

# ANSI color constant escape sequences:
ANSI_PRE = '\x1b['
ANSI_POST = 'm'
ANSI_RESET = ANSI_PRE + '0' + ANSI_POST
BLACK = 30
RED = 31
GREEN = 32
YELLOW = 33
BLUE = 34
PURPLE = 35
CYAN = 36
WHITE = 37

# Option flags set by user at cli

# use ANSI color sequences
USE_COLOR = False

# add color to the game's timestamp
COLOR_TIME = False

# use a black background
BLACK_BACKGROUND = False

# use bright (or bold) colors
USE_BRIGHT = False


def color(clr, text):
    """
        function to wrap ANSI escape sequences around text
        to set the display color of the text

        :param clr: one of the color constants above
        :param text: the text string to color
        :return: the text with the proper ANSI prefix and suffix bytes
    """
    if not USE_COLOR:
        return text
    background_color = ''
    if BLACK_BACKGROUND:
        background_color = ';40'
    prefix = '0;'
    if USE_BRIGHT:
        prefix = '1;'

    return ''.join([ANSI_PRE, prefix, str(clr), background_color, ANSI_POST, text, ANSI_RESET])


def test_ansi_colors():
    """
    print out all combinations of ANSI color foregrounds and backgrounds
    """
    for foreground in range(30, 38):
        output = ''
        str_f = str(foreground)
        for background in range(40, 48):
            str_b = str(background)
            output += ''.join([ANSI_PRE, str_f, ';', str_b, ANSI_POST, str_f, '/', str_b])
        print(output + ANSI_RESET)


def datetime_from_utc_to_local(utc_datetime):
    """
    convert a datetime from UTC to local time
    :param utc_datetime: datetime object of the game start time in UTC
    :return: returns the datetime converted from UTC to local time
    """
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


def get_game_time(game):
    """
    get the game time in local time
    :param game: dictionary of a specific game
    :return: returns the game start time converted from UTC to local time
    """
    game_time_str = game['gameDate']  # 2018-03-03T18:00:00Z
    game_time = datetime.strptime(game_time_str, '%Y-%m-%dT%H:%M:%SZ')

    return datetime_from_utc_to_local(game_time)


def get_teams(game):
    """
    retrieve the two teams in this game and the notations indicating
    if a favorite or rival team is involved
    :param game: dictionary of a specific game
    :return: returns a tuple containing team1, team2, and the game notations
    """
    team1 = game['teams']['away']['team']['name']
    team2 = game['teams']['home']['team']['name']
    note1 = ' '
    note2 = ' '

    # if team1.find('Canadiens') >= 0:
    #     team1 = 'Montreal Canadiens'
    # if team2.find('Canadiens') >= 0:
    #     team2 = 'Montreal Canadiens'

    if team1 in FAVORITES or team2 in FAVORITES:
        note1 = '*'
    if team1 in RIVALS or team2 in RIVALS:
        note2 = '!'

    # Add optional ANSI color sequences to favorite and rival team names
    if team1 in FAVORITES:
        team1 = color(GREEN, team1)
    if team2 in FAVORITES:
        team2 = color(GREEN, team2)
    if team1 in RIVALS:
        team1 = color(RED, team1)
    if team2 in RIVALS:
        team2 = color(RED, team2)

    return team1, team2, note1 + note2


def create_games_dict(all_games):
    """
    create a dictionary of today's games with formatted descriptions
    :param all_games: dictionary of today's games retrieved from the web api
    :return: returns a dictionary of today's games with formatted descriptions
    """
    game_dictionary = {}
    at_str = color(WHITE, ' at ')
    for game in all_games:
        # get local time for game
        game_time = get_game_time(game)

        # Get lowercase version of 'AM/PM'
        am_pm_str = game_time.strftime('%p').lower()

        # Create game time string
        game_time_str = game_time.strftime('%I:%M ' + am_pm_str)
        if COLOR_TIME:
            game_time_str = color(BLUE, game_time_str)

        # Get the teams involved
        (team1, team2, notations) = get_teams(game)

        # Create the game description string
        game_desc_str = ''.join([color(WHITE, notations + '   '),
                                 game_time_str, '  -  ', team1,
                                 at_str, team2])

        # Add the game to the games dictionary indexed by game start time
        gametime_key = game_time.strftime('%H:%M') + team1
        game_dictionary[gametime_key] = game_desc_str

    return game_dictionary


def create_test_data_file(filename, json_data):
    """
    create a file containing test data to use as input during unit tests
    :param filename: the file name to write the data to
    :param json_data: the json data to write to the test input file
    """
    json_str = str(json_data).replace("'", '"')
    json_str = json_str.replace('False', '"False"')
    json_str = json_str.replace('True', '"True"')
    if json_str[0] == "'" and json_str[-1] == "'":
        json_str = json_str[1:-1]
    with open(filename, 'wt') as filehandle:
        filehandle.write(json_str)


def get_json_data(api_url):
    """
    retrieve the json data returned from the specified REST url
    :param api_url: the url to retrieve the data from
    :return: returns the json data as a string
    """
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    # ssl._create_default_https_context = ssl._create_unverified_context
    with urllib.request.urlopen(api_url, context=ssl_context) as url:
        http_info = url.info()
        raw_data = url.read().decode(http_info.get_content_charset())
        json_data = json.loads(raw_data)
        return json_data
#   create_test_data_file('test.json', json_data)
    return {}


def get_games_count(json_data):
    """
    get the number of games contained in the specified json data
    :param json_data: a string containing the json data retrieved from a previous web REST api call
    :return: returns the total number of games (0 if there are none)
    """
    total_games = 0
    if 'totalGames' in json_data:
        total_games = int(json_data['totalGames'])
    return total_games


def get_todays_games(json_data):
    """
    create a dictionary of game description string
    values with start time keys. Also create a list
    of those keys sorted in ascending start time order.

    :param json_data: dictionary of games data from the web
    :return: returns a tuple of the game_dict, display_keys
    """
    # Sort the games based on start time
    if not 'dates' in json_data or not json_data['dates']:
        return {}, {}
    all_games = json_data['dates'][0]['games']
    game_dictionary = create_games_dict(all_games)
    sorted_games = sorted(game_dictionary.keys())
    return game_dictionary, sorted_games


def output_todays_games(games_dict, key_list, sport_name):
    """
    output today's games in ascending order by their start times

    :param games_dict: the dictionary of game times to game descriptions
    :param key_list: list of gametime keys sorted in ascending order
    :param sport_name: game type string used in case the are no games
    :return: returns nothing
    """
    if not games_dict or not key_list:
        output = ''
        if sport_name == 'hockey':
            output = 'Sorry.  '  # think like a Canadian :)
        output += ''.join(['There are no ', sport_name, ' games today'])
        print(color(WHITE, '     ' + output))
        return
    for key in key_list:
        print(games_dict[key])


# parse and process the command line
def process_command_line(argv):
    """
    process the command line options arguments
    :param argv: list of arguments passed on the command line
    """
    global USE_COLOR, BLACK_BACKGROUND, COLOR_TIME, USE_BRIGHT
    nhl_api_url = 'https://statsapi.web.nhl.com/api/v1/schedule'
    mlb_api_url = 'https://statsapi.mlb.com/api/v1/schedule?sportId=1'
    json_data = {}
    sport_name = ''

    for cmd in argv[1:]:
        cmd = cmd.upper()
        USE_COLOR = True if cmd == 'C' else USE_COLOR
        USE_BRIGHT = True if cmd == 'I' else USE_BRIGHT
        BLACK_BACKGROUND = True if cmd == 'K' else BLACK_BACKGROUND
        COLOR_TIME = True if cmd == 'T' else COLOR_TIME
        USE_COLOR = False if cmd == 'N' else USE_COLOR

        if cmd == 'H':
            json_data = get_json_data(nhl_api_url)
            sport_name = 'hockey'
        if cmd == 'B':
            json_data = get_json_data(mlb_api_url)
            sport_name = 'baseball'

    if json_data:
        games_dict, keys = get_todays_games(json_data)
        output_todays_games(games_dict, keys, sport_name)


if __name__ == "__main__":
    process_command_line(sys.argv)
