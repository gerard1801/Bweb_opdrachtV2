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
from bokeh.plotting import figure, output_file, show, save
from bokeh.models import OpenURL, TapTool, ColumnDataSource, HoverTool
from bokeh.models.callbacks import CustomJS
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.resources import CDN
from bokeh.embed import file_html

import sqlite3

# Create your views here.
def Club(request):
    conn = sqlite3.connect('/Users/gerardvanderwel/Downloads/database.sqlite')
    c = conn.cursor()
    data = {}
    club_data = {}
    season_data = {}

    if request.method == 'POST':
        if request.POST.get('flag-btn'):
            flag_id = request.POST['flag-btn'][:]
            c.execute("SELECT DISTINCT team_long_name, team_api_id FROM Team WHERE team_api_id IN (SELECT DISTINCT home_team_api_id FROM Match WHERE league_id=?)", (flag_id,))
            data = c.fetchall()
            print(data)
    if request.method == 'POST':
        if request.POST.get('club-btn'):
            global club_id
            club_id = request.POST['club-btn'][:]
            c.execute("SELECT DISTINCT season FROM Match WHERE home_team_api_id IN (SELECT team_api_id FROM Team WHERE team_long_name == ?)", (club_id,))
            club_data = c.fetchall()
            print(club_data)
    if request.method == 'POST':
        if request.POST.get('season-btn'):
            season_id = request.POST['season-btn'][:]

            print(club_id)

            c.execute("SELECT team_api_id FROM Team WHERE team_long_name == ?", (club_id,))
            new_id = c.fetchall()
            new_id = (new_id[0][0])
            c.execute("SELECT m.match_api_id, m.home_team_api_id, m.away_team_api_id, t.team_long_name, t2.team_long_name FROM Match m INNER JOIN Team t ON m.home_team_api_id=t.team_api_id INNER JOIN Team t2 ON m.away_team_api_id=t2.team_api_id WHERE m.home_team_api_id=? AND m.season=? OR m.away_team_api_id=? AND m.season=?", (new_id, season_id, new_id, season_id,))
            season_data = c.fetchall()
            print(season_data)
    if request.method == 'POST':
        if request.POST.get('match-btn'):
            global match_id
            match_id = request.POST['match-btn'][:]
            print(match_id)
            request.session['match_id'] = match_id
            return HttpResponseRedirect('/match')



    return render(request, 'Club.html', {
        'data': data,
        'club_data': club_data,
        'season_data': season_data,
    })

def Match(request):
    database = '/Users/gerardvanderwel/Downloads/database.sqlite'
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    print("match_ID")
    print(match_id)
    tables = pd.read_sql("""SELECT *
                                    FROM Match 
                                    WHERE match_api_id=1988797;""", conn)
    match_api_id = 1988797
    sql = 'SELECT * From MATCH WHERE match_api_id=?'
    cur.execute(sql, (match_id,))
    match = cur.fetchone()
    print(match)

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

    home_players_x = [5 if x == 1 else x for x in home_players_x]
    away_players_x = [5 if x == 1 else x for x in away_players_x]

    home_plot_x = []
    home_plot_y = []
    for i in home_players_x:
        home_plot_x.append(i * 50)
    for i in home_players_y:
        home_plot_y.append(i * 50)

    output_file("line.html")
    p = figure(x_range=(0, 500), y_range=(0, 600), tools="tap")
    p.image_url(url=['/static/images/Soccer_Field_Transparant.png'], x=0, y=600, w=500, h=600)
    p.circle(home_plot_x, home_plot_y, size=20)
    taptool = p.select(type=TapTool)
    taptool.callback = CustomJS(code="""          
                window.open("http://127.0.0.1:8000/player" ,"_self");
                """)
    p.axis.visible = False
    p.grid.visible = False
    p.toolbar_location = None
    output_file("templates/bokeh2.html")
    save(p)


    return render(request, 'Match.html')

def Player(request):
    return render(request, 'Player.html')

def Home(request):
    return render(request, 'bokeh.html')








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
                                WHERE match_api_id=1988797;""", conn)
    match_api_id = 1988797
    sql = 'SELECT * From MATCH WHERE match_api_id=?'
    cur.execute(sql, (match_api_id,))
    match = cur.fetchone()
    print(match)

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

    home_players_x = [5 if x == 1 else x for x in home_players_x]
    away_players_x = [5 if x == 1 else x for x in away_players_x]

    datafile = cbook.get_sample_data(
        '/Users/gerardvanderwel/PycharmProjects/Bweb_opdrachtV2/opdracht/static/images/Soccer_Field_Transparant.png')


    home_plot_x = []
    home_plot_y = []
    for i in home_players_x:
        home_plot_x.append(i * 50)
    for i in home_players_y:
        home_plot_y.append(i * 50)

    output_file("line.html")
    p = figure(title="opstelling", x_range=(0,500), y_range=(0,600), tools="tap")
    p.image_url(url=['/static/images/Soccer_Field_Transparant.png'], x=0, y=600, w=500, h=600)
    p.circle(home_plot_x, home_plot_y, size=20)
    url = "Player.html"
    taptool = p.select(type=TapTool)
    taptool.callback = CustomJS(code="""          
            window.open("http://127.0.0.1:8000/player" ,"_self");
            """)
    output_file("templates/bokeh2.html")
    save(p)

    return render(request, 'Player.html')

