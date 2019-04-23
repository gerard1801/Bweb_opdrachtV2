from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from scipy.misc import imread
import matplotlib.cbook as cbook
from django.db import connection
import sqlite3

# Create your views here.
def Club(request):
    conn = sqlite3.connect('/Users/gerardvanderwel/Downloads/database.sqlite')
    c = conn.cursor()
    data = {}
    club_data = {}
    if request.method == 'POST':
        if request.POST.get('flag-btn'):
            flag_id = request.POST['flag-btn'][:]
            c.execute("SELECT DISTINCT team_long_name FROM Team WHERE team_api_id IN (SELECT DISTINCT home_team_api_id FROM Match WHERE league_id=?)", (flag_id,))
            data = c.fetchall()
            print(data)
    if request.method == 'POST':
        if request.POST.get('club-btn'):
            club_id = request.POST['club-btn'][:]
            c.execute("SELECT DISTINCT season FROM Match WHERE home_team_api_id IN (SELECT team_api_id FROM Team WHERE team_long_name == ?)", (club_id,))
            club_data = c.fetchall()
            print(club_data)
    return render(request, 'Club.html', {
        'data': data,
        'club_data': club_data,
    })

def Match(request):
    return render(request, 'Match.html')

def Player(request):
    return render(request, 'Player.html')

def Home(request):
    return render(request, 'Home.html')


def Opstelling(request):
    database = '/Users/gerardvanderwel/Downloads/database.sqlite'
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    tables = pd.read_sql("""SELECT *
                            FROM Match 
                            WHERE match_api_id=1989903;""", conn)
    match_api_id = 1989903
    sql = 'SELECT * From MATCH WHERE match_api_id=?'
    cur.execute(sql, (match_api_id,))
    match = cur.fetchone()

    home_players_api_id = list()
    away_players_api_id = list()
    home_players_x = list()
    away_players_x = list()
    home_players_y = list()
    away_players_y = list()

    for i in range(1, 12):
        home_players_api_id.append(match['home_player_%d' % i])
        away_players_api_id.append(match['away_player_%d' % i])
        home_players_x.append(match['home_player_X%d' % i])
        away_players_x.append(match['away_player_X%d' % i])
        home_players_y.append(match['home_player_Y%d' % i])
        away_players_y.append(match['away_player_Y%d' % i])

    print('Example, home players api id: ')
    print(home_players_api_id)

    players_api_id = [home_players_api_id, away_players_api_id]
    players_api_id.append(home_players_api_id)  # Home
    players_api_id.append(away_players_api_id)  # Away
    players_names = [[None] * 11, [None] * 11]

    for i in range(2):
        players_api_id_not_none = [x for x in players_api_id[i] if x is not None]
        sql = 'SELECT player_api_id,player_name FROM Player'
        sql += ' WHERE player_api_id IN (' + ','.join(map(str, players_api_id_not_none)) + ')'
        cur.execute(sql)
        players = cur.fetchall()
        for player in players:
            idx = players_api_id[i].index(player['player_api_id'])
            name = player['player_name'].split()[-1]  # keep only the last name
            players_names[i][idx] = name

    print('Home team players names:')
    print(players_names[0])
    print('Away team players names:')
    print(players_names[1])

    home_players_x = [5 if x == 1 else x for x in home_players_x]
    away_players_x = [5 if x == 1 else x for x in away_players_x]


    # Home team (in blue)
    plt.subplot(2, 1, 1)
    plt.rc('grid', linestyle="-", color='black')
    plt.rc('figure', figsize=(12, 20))
    plt.gca().invert_yaxis()  # Invert y axis to start with the goalkeeper at the top
    for label, x, y in zip(players_names[0], home_players_x, home_players_y):
        plt.annotate(
            label,
            xy=(x, y), xytext=(-20, 20),
            textcoords='offset points', va='bottom')
    plt.scatter(home_players_x, home_players_y, s=100, c='blue')
    plt.grid(True)

    datafile = cbook.get_sample_data(
        '/Users/gerardvanderwel/PycharmProjects/Bweb_opdrachtV2/opdracht/static/images/Soccer_Field_Transparant.png')
    img = imread(datafile)
    #plt.scatter(x, y, zorder=1)
    plt.imshow(img, zorder=0, extent=[1.0, 9.0, 1.0, 7.0])
    # plt.show()
    plt.savefig("./static/images/line-up2.png")

    # Away team (in red)
    plt.subplot(2, 1, 2)
    plt.rc('grid', linestyle="-", color='black')
    plt.rc('figure', figsize=(12, 20))
    plt.gca().invert_xaxis()  # Invert x axis to have right wingers on the right
    for label, x, y in zip(players_names[1], away_players_x, away_players_y):
        plt.annotate(
            label,
            xy=(x, y), xytext=(-20, 20),
            textcoords='offset points', va='bottom')
    plt.scatter(away_players_x, away_players_y, s=480, c='red')
    plt.grid(True)

    ax = [plt.subplot(2, 2, i + 1) for i in range(0)]
    for a in ax:
        a.set_xticklabels([])
        a.set_yticklabels([])
    plt.subplots_adjust(wspace=0, hspace=0)
    plt.savefig("./static/images/line-up.png")


    players_y = [home_players_y, away_players_y]
    formations = [None] * 2
    for i in range(2):
        formation_dict = Counter(players_y[i]);
        sorted_keys = sorted(formation_dict)
        formation = ''
        for key in sorted_keys[1:-1]:
            y = formation_dict[key]
            formation += '%d-' % y
        formation += '%d' % formation_dict[sorted_keys[-1]]
        formations[i] = formation

    print('Home team formation: ' + formations[0])
    print('Away team formation: ' + formations[1])

    np.random.seed(0)
    x = np.random.uniform(0.0, 10.0, 15)
    y = np.random.uniform(0.0, 10.0, 15)



    return render(request, 'Match.html')


def test(request):
    database = '/Users/gerardvanderwel/Downloads/database.sqlite'
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    tables = pd.read_sql("""SELECT *
                                FROM Match 
                                WHERE match_api_id=1032882;""", conn)
    match_api_id = 1032882
    sql = 'SELECT * From MATCH WHERE match_api_id=?'
    cur.execute(sql, (match_api_id,))
    match = cur.fetchone()

    home_players_api_id = list()
    away_players_api_id = list()
    home_players_x = list()
    away_players_x = list()
    home_players_y = list()
    away_players_y = list()

    for i in range(1, 12):
        home_players_api_id.append(match['home_player_%d' % i])
        away_players_api_id.append(match['away_player_%d' % i])
        home_players_x.append(match['home_player_X%d' % i])
        away_players_x.append(match['away_player_X%d' % i])
        home_players_y.append(match['home_player_Y%d' % i])
        away_players_y.append(match['away_player_Y%d' % i])

    print('Example, home players api id: ')
    print(home_players_api_id)

    players_api_id = [home_players_api_id, away_players_api_id]
    players_api_id.append(home_players_api_id)  # Home
    players_api_id.append(away_players_api_id)  # Away
    players_names = [[None] * 11, [None] * 11]

    for i in range(2):
        players_api_id_not_none = [x for x in players_api_id[i] if x is not None]
        sql = 'SELECT player_api_id,player_name FROM Player'
        sql += ' WHERE player_api_id IN (' + ','.join(map(str, players_api_id_not_none)) + ')'
        cur.execute(sql)
        players = cur.fetchall()
        for player in players:
            idx = players_api_id[i].index(player['player_api_id'])
            name = player['player_name'].split()[-1]  # keep only the last name
            players_names[i][idx] = name

    print('Home team players names:')
    print(players_names[0])
    print('Away team players names:')
    print(players_names[1])

    home_players_x = [5 if x == 1 else x for x in home_players_x]
    away_players_x = [5 if x == 1 else x for x in away_players_x]

    datafile = cbook.get_sample_data(
        '/Users/gerardvanderwel/PycharmProjects/Bweb_opdrachtV2/opdracht/static/images/Soccer_Field_Transparant.png')
    img = imread(datafile)
    fig, ax = plt.subplots()
    x = [0, 10, 100]
    # plt.scatter(x, y, zorder=1)
    ax.imshow(img, extent=[0.0, 100.0, 0.0, 120.0])
    print('Home players: ' + str(home_players_x))
    home_plot_x = []
    home_plot_y = []
    for i in home_players_x:
        home_plot_x.append(i * 10)
    for i in home_players_y:
        home_plot_y.append(i * 10)

    print(home_plot_x)
    print(home_plot_y)
    print('Home players: ' + str(home_players_x))
    ax.plot(home_plot_x, home_plot_y, 'ro', color='firebrick')
    for label, x, y in zip(players_names[0], home_plot_x, home_plot_y):
        ax.annotate(
            label,
            xy=(x, y), xytext=(-10, 5),
            textcoords='offset points', va='bottom')
    #ax.scatter(home_players_x, home_players_y, s=100, c='blue')
    # ax.set_xticks([])
    plt.savefig("./static/images/test.png")
    return render(request, 'Match.html')
'''
    plt.subplot(2, 1, 1)
    plt.rc('grid', linestyle="-", color='black')
    plt.rc('figure', figsize=(12, 20))
    plt.gca().invert_yaxis()  # Invert y axis to start with the goalkeeper at the top
    for label, x, y in zip(players_names[0], home_players_x, home_players_y):
        plt.annotate(
            label,
            xy=(x, y), xytext=(-20, 20),
            textcoords='offset points', va='bottom')
    plt.scatter(home_players_x, home_players_y, s=100, c='blue')
    plt.grid(True)
'''
