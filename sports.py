# sports.py

"""
A python script to retrieve and print
the day's hockey and/or baseball games
"""

# 2018 - ++tmw

import sys
import ssl
import urllib.request
import json
from datetime import datetime
import time


# Set up lists of favorite teams and rival teams for both hockey and basebaall
favorites = [   'Dallas Stars', 'Pittsburgh Penguins', 'Detroit Red Wings', 'Arizona Coyotes', 'Calgary Flames',
                'Texas Rangers', 'Houston Astros']

rivals    = [   'Nashville Predators', 'Winnipeg Jets', 'Minnesota Wild', 'Colorado Avalanche', 'St Louis Blues', 'Chicago Blackhawks',
                'Los Angeles Angels', 
#               'Houston Astros', 
                'Seattle Mariners', 'Oakland Athletics']

# ANSI color constant escape sequences:
ANSI_PRE   = '\x1b['
ANSI_POST  = 'm'
ANSI_RESET = ANSI_PRE + '0' + ANSI_POST
BLACK      = 30
RED        = 31
GREEN      = 32
YELLOW     = 33
BLUE       = 34
PURPLE     = 35
CYAN       = 36
WHITE      = 37

# Option flags set by user at cli

# use ANSI color sequences
use_color = False

# add color to the game's timestamp
color_time = False

# use a black background
black_bkgnd = False

# use bright (or bold) colors
use_bright = False


def color(clr, text):
    """
        function to wrap ANSI escape sequences around text
        to set the display color of the text

        :param clr: one of the color constants above
        :param text: the text string to color
        :return: the text with the proper ANSI prefix and suffix bytes
    """
    global ANSI_PRE, ANSI_PORT, ANSI_RESET, use_color, black_bkgnd, use_bright
    if not use_color : return text
    bkgnd_color = ''
    if black_bkgnd : bkgnd_color = ';40'
    prefix = '0;'
    if use_bright : prefix = '1;'

    return ANSI_PRE + prefix + str(clr) + bkgnd_color + ANSI_POST + text + ANSI_RESET


def test_ansi_colors():
    global ANSI_PRE, ANSI_POST, ANSI_RESET
    for foreground in range(30, 38):
        output = ''
        str_f = str(foreground)
        for background in range(40, 48):
            str_b = str(background)
            output += ANSI_PRE + str_f + ';' + str_b + ANSI_POST + str_f + '/' + str_b
        print(output + ANSI_RESET)

def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset

def get_game_time(game):
    global from_zone, to_zone
    game_time_str = game['gameDate']    # 2018-03-03T18:00:00Z
    game_time = datetime.strptime(game_time_str, '%Y-%m-%dT%H:%M:%SZ')

    return datetime_from_utc_to_local(game_time)


def get_teams(game):
    global favorites, rivals
    team1 = game['teams']['away']['team']['name']
    team2 = game['teams']['home']['team']['name']
    note1 = ' '
    note2 = ' '
 
    if team1.find('Canadiens') >= 0 : team1 = 'Montreal Canadiens'
    if team2.find('Canadiens') >= 0 : team2 = 'Montreal Canadiens'

    if team1 in favorites or team2 in favorites : note1 = '*'
    if team1 in rivals or team2 in rivals : note2 = '!'

    # Add optional ANSI color sequences to favs and rivals team names
    if team1 in favorites : team1 = color(GREEN, team1)
    if team2 in favorites : team2 = color(GREEN, team2)
    if team1 in rivals : team1 = color(RED, team1)
    if team2 in rivals : team2 = color(RED, team2)

    return (team1, team2, note1 + note2)


def create_games_dict(all_games):
    global WHITE, BLUE
    game_dictionary = {}
    at_str = color(WHITE, ' at ')
    for game in all_games:
        # get local time for game
        game_time = get_game_time(game)

        # Get lowercase version of 'AM/PM'
        am_pm_str = game_time.strftime('%p').lower()

        # Create game time string
        game_time_str = game_time.strftime('%I:%M ' + am_pm_str)
        if color_time : game_time_str = color(BLUE, game_time_str)
    
        # Get the teams involved
        (team1, team2, notations) = get_teams(game)

        # Create the game description string
        game_desc_str = color(WHITE, notations + '   ') + game_time_str + '  -  ' + team1 + at_str + team2
    
        # Add the game to the games dictionary indexed by game start time
        game_dictionary[game_time.strftime('%H:%M') + team1] = game_desc_str

    return game_dictionary


def print_todays_games(api_url, game_name):
    global WHITE

    ssl._create_default_https_context = ssl._create_unverified_context

    response = urllib.request.urlopen(api_url)
    json_data = json.load(response)
    
    if 0 == json_data['totalGames']:
        output = ''
        if game_name == 'hockey' : output += 'Sorry.  '
        output += 'There are no ' + game_name + ' games today'
        print(color(WHITE, '     ' + output))
        return

    # Sort the games based on start time and print them
    all_games = json_data['dates'][0]['games']

    game_dictionary = create_games_dict(all_games)
    for game_time in sorted(game_dictionary.keys()):
        print(game_dictionary[game_time])


# parse and process the command line
def process_command_line(argv):
    global use_color, black_bkgnd, color_time, use_bright

    index = 1
    while (len(argv) > index):
        cmd = argv[index].upper()
        index += 1
        if 'C' == cmd : use_color   = True
        if 'I' == cmd : use_bright  = True
        if 'K' == cmd : black_bkgnd = True
        if 'T' == cmd : color_time  = True
        if 'N' == cmd : use_color   = False
        if 'H' == cmd :
            api_url = 'https://statsapi.web.nhl.com/api/v1/schedule'
            print_todays_games(api_url, 'hockey')
        if 'B' == cmd :
            api_url = 'https://statsapi.mlb.com/api/v1/schedule?sportId=1'
            print_todays_games(api_url, 'baseball')


process_command_line(sys.argv)
#test_ansi_colors()
