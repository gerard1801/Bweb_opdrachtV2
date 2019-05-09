from operator import itemgetter

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect
from bokeh.plotting import figure, output_file, save
from bokeh.models import OpenURL, TapTool, ColumnDataSource, HoverTool, Tap
from bokeh.models.callbacks import CustomJS
from bokeh.embed import file_html
from bokeh.resources import CDN


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
        print(request.POST)
        if request.POST.get('match-btn'):
            global match_id
            match_id = request.POST['match-btn'][:]
            print(match_id)
            print(request.POST)

            #return HttpResponseRedirect('/match')
    return render(request, 'Club.html', {
        'data': data,
        'club_data': club_data,
        'season_data': season_data,
    })




def Match(request):
    try:
        database = '/Users/gerardvanderwel/Downloads/database.sqlite'
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        print("match_ID")
        print(match_id)
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
        away_plot_x = []
        away_plot_y = []
        for i in home_players_x:
            home_plot_x.append(i * 50)
        for i in home_players_y:
            home_plot_y.append(i * 50)
        for i in away_players_x:
            away_plot_x.append(i * 50)
        for i in away_players_y:
            away_plot_y.append(i * 50)

        cord_sort = [list(x) for x in zip(*sorted(zip(home_plot_y, home_plot_x), key=lambda x: (x[0], -x[1])))]
        cord_sort2 = [list(x) for x in zip(*sorted(zip(away_plot_y, away_plot_x), key=lambda x: (x[0], -x[1])))]
        url1 = "http://127.0.0.1:8000/player/"
        urls = []
        for i in range(len(players_api_id[0])):
            urls.append(url1 + str(players_api_id[0][i]))
        output_file("line.html")
        source = ColumnDataSource(data=dict(x=cord_sort[1], y=cord_sort[0], home_names=players_names[0],
                                            url=urls))
        hover = HoverTool(tooltips=[
            ("(x,y)", "(@x, @y)"),
            ('Name', '@home_names')
        ])
        p = figure(x_range=(0, 500), y_range=(0, 600), tools=[hover, "tap"])
        p.image_url(url=['/static/images/Soccer_Field_Transparant.png'], x=0, y=600, w=500, h=600)
        p.circle('x', 'y', size=20, source=source)
        taptool = p.select(type=TapTool)

        taptool.callback = CustomJS(args=dict(source=source), code="""
                    selection = require("core/util/selection")
                    indices = selection.get_indices(source)
                    url = source.data['url'][indices]
                    window.open(url ,"_self");
                    """)
        p.axis.visible = False
        p.grid.visible = False
        p.toolbar_location = None
        output_file("templates/bokeh_thuis.html")
        save(p)

        hover2 = HoverTool(tooltips=[
            ("(x,y)", "(@x, @y)"),
            ('Name', '@home_names')
        ])
        source2 = ColumnDataSource(data=dict(x=cord_sort2[1], y=cord_sort2[0], home_names=players_names[1], url=urls))
        p2 = figure(x_range=(0, 500), y_range=(0, 600), tools=[hover2, "tap"])
        p2.image_url(url=['/static/images/Soccer_Field_Transparant.png'], x=0, y=600, w=500, h=600)
        p2.circle('x', 'y', size=20, source=source2)
        taptool2 = p2.select(type=TapTool)
        taptool2.callback = CustomJS(args=dict(source=source2), code="""
                                            selection = require("core/util/selection")
                                            indices = selection.get_indices(source)
                                            url = source.data['url'][indices]
                                            window.open(url ,"_self");
                                            """)
        p2.axis.visible = False
        p2.grid.visible = False
        p2.toolbar_location = None
        output_file("templates/bokeh_uit.html")
        save(p2)



        #match gegevens
        conn = sqlite3.connect('/Users/gerardvanderwel/Downloads/database.sqlite')
        c = conn.cursor()
        thuis_goals = c.execute("SELECT home_team_goal FROM MATCH WHERE match_api_id=?", (match_id,))
        thuis_goals = thuis_goals.fetchall()
        print(thuis_goals)
        uit_goals = c.execute("SELECT away_team_goal FROM MATCH WHERE match_api_id=?", (match_id,))
        uit_goals = uit_goals.fetchall()
        print(uit_goals)
        thuis_team = c.execute("SELECT team_long_name FROM Team WHERE team_api_id IN(SELECT home_team_api_id from Match WHERE match_api_id=?)", (match_id,))
        thuis_team = thuis_team.fetchall()
        uit_team = c.execute("SELECT team_long_name FROM Team WHERE team_api_id IN(SELECT away_team_api_id from Match WHERE match_api_id=?)",(match_id,))
        uit_team = uit_team.fetchall()
        thuis_api = c.execute("SELECT home_team_api_id from Match WHERE match_api_id=?", (match_id,))
        thuis_api = thuis_api.fetchall()
        uit_api = c.execute("SELECT away_team_api_id from Match WHERE match_api_id=?", (match_id,))
        uit_api = uit_api.fetchall()

    #fouls berekenen
        fouls = c.execute("SELECT foulcommit FROM Match WHERE match_api_id=?", (match_id,))
        fouls = fouls.fetchall()
        fouls_str = fouls[0][0]
        fouls_str = fouls_str.split("<team>")
        new_list = []
        for x in fouls_str:
            new_list.append(x.split("</team>"))
        new_list.pop(0)
        for i in range(len(new_list)):
            new_list[i].pop(1)
        lijst = [' '.join([str(c) for c in lst]) for lst in new_list]
        thuis_fouls = 0
        uit_fouls = 0
        for i in lijst:
            if i == str(thuis_api[0][0]):
                thuis_fouls += 1
            elif i == str(uit_api[0][0]):
                uit_fouls += 1

    #shots on target berekenen
        shoton = c.execute("SELECT shoton FROM Match WHERE match_api_id=?", (match_id,))
        shoton = shoton.fetchall()
        shoton_str = shoton[0][0]
        shoton_str = shoton_str.split("<team>")
        shot_list = []
        for x in shoton_str:
            shot_list.append(x.split("</team>"))
        shot_list.pop(0)
        for i in range(len(shot_list)):
            shot_list[i].pop(1)
        lijst2 = [' '.join([str(c) for c in lst]) for lst in shot_list]
        thuis_shots = 0
        uit_shots = 0
        for i in lijst2:
            if i == str(thuis_api[0][0]):
                thuis_shots += 1
            elif i == str(uit_api[0][0]):
                uit_shots += 1

    #shots off target berekenen
        shotoff = c.execute("SELECT shotoff FROM Match WHERE match_api_id=?", (match_id,))
        shotoff = shotoff.fetchall()
        shotoff_str = shotoff[0][0]
        shotoff_str = shotoff_str.split("<team>")
        shotoff_list = []
        for x in shotoff_str:
            shotoff_list.append(x.split("</team>"))
        shotoff_list.pop(0)
        for i in range(len(shotoff_list)):
            shotoff_list[i].pop(1)
        lijst3 = [' '.join([str(c) for c in lst]) for lst in shotoff_list]
        thuis_shotsoff = 0
        uit_shotsoff = 0
        for i in lijst3:
            if i == str(thuis_api[0][0]):
                thuis_shotsoff += 1
            elif i == str(uit_api[0][0]):
                uit_shotsoff += 1

    #crosses per team
        crosses = c.execute("SELECT cross FROM Match WHERE match_api_id=?", (match_id,))
        crosses = crosses.fetchall()
        crosses_str = crosses[0][0]
        crosses_str = crosses_str.split("<team>")
        crosses_list = []
        for x in crosses_str:
            crosses_list.append(x.split("</team>"))
        crosses_list.pop(0)
        for i in range(len(crosses_list)):
            crosses_list[i].pop(1)
        lijst4 = [' '.join([str(c) for c in lst]) for lst in crosses_list]
        thuis_crosses = 0
        uit_crosses = 0
        for i in lijst4:
            if i == str(thuis_api[0][0]):
                thuis_crosses += 1
            elif i == str(uit_api[0][0]):
                uit_crosses += 1

    #corners per team
        corners = c.execute("SELECT corner FROM Match WHERE match_api_id=?", (match_id,))
        corners = corners.fetchall()
        corners_str = corners[0][0]
        corners_str = corners_str.split("<team>")
        corners_list = []
        for x in corners_str:
            corners_list.append(x.split("</team>"))
        corners_list.pop(0)
        for i in range(len(corners_list)):
            corners_list[i].pop(1)
        lijst5 = [' '.join([str(c) for c in lst]) for lst in corners_list]
        thuis_corners = 0
        uit_corners = 0
        for i in lijst5:
            if i == str(thuis_api[0][0]):
                thuis_corners += 1
            elif i == str(uit_api[0][0]):
                uit_corners += 1

    #possesion per team
        possession = c.execute("SELECT possession FROM Match WHERE match_api_id=?", (match_id,))
        possession = possession.fetchall()
        possession_str = possession[0][0]
        possession_str = possession_str.split("<homepos>")
        possession_list = []
        for x in possession_str:
            possession_list.append(x.split("</homepos>"))
        possession_list.pop(0)
        home_pos = possession_list[-1][0]
        away_pos = 100 - int(home_pos)

        btu = request.POST.get('radio')
        print(btu)

        if btu == "Beide":
            return render(request, 'Match.html', {
                'thuis_goals': thuis_goals,
                'uit_goals': uit_goals,
                'thuis_team': thuis_team,
                'uit_team': uit_team,
                'thuis_fouls': thuis_fouls,
                'uit_fouls': uit_fouls,
                'thuis_shotson': thuis_shots,
                'uit_shotson': uit_shots,
                'thuis_shotsoff': thuis_shotsoff,
                'uit_shotsoff': uit_shotsoff,
                'thuis_crosses': thuis_crosses,
                'uit_crosses': uit_crosses,
                'thuis_corners': thuis_corners,
                'uit_corners': uit_corners,
                'home_pos': home_pos,
                'away_pos': away_pos,
            })
        elif btu == "Thuis":
            return render(request, "Match_tu.html", {
                'thuis_goals': thuis_goals,
                'uit_goals': uit_goals,
                'thuis_team': thuis_team,
                'uit_team': uit_team,
                'thuis_fouls': thuis_fouls,
                'uit_fouls': uit_fouls,
                'thuis_shotson': thuis_shots,
                'uit_shotson': uit_shots,
                'thuis_shotsoff': thuis_shotsoff,
                'uit_shotsoff': uit_shotsoff,
                'thuis_crosses': thuis_crosses,
                'uit_crosses': uit_crosses,
                'thuis_corners': thuis_corners,
                'uit_corners': uit_corners,
                'home_pos': home_pos,
                'away_pos': away_pos,
            })
        elif btu == "Uit":
            return render(request, "Match_ui.html", {
                'thuis_goals': thuis_goals,
                'uit_goals': uit_goals,
                'thuis_team': thuis_team,
                'uit_team': uit_team,
                'thuis_fouls': thuis_fouls,
                'uit_fouls': uit_fouls,
                'thuis_shotson': thuis_shots,
                'uit_shotson': uit_shots,
                'thuis_shotsoff': thuis_shotsoff,
                'uit_shotsoff': uit_shotsoff,
                'thuis_crosses': thuis_crosses,
                'uit_crosses': uit_crosses,
                'thuis_corners': thuis_corners,
                'uit_corners': uit_corners,
                'home_pos': home_pos,
                'away_pos': away_pos,
            })
    except Exception as e:
        print(e)
        return render(request, "no_data.html")


    return render(request, 'Match.html', {
        'thuis_goals': thuis_goals,
        'uit_goals': uit_goals,
        'thuis_team': thuis_team,
        'uit_team': uit_team,
        'thuis_fouls': thuis_fouls,
        'uit_fouls': uit_fouls,
        'thuis_shotson': thuis_shots,
        'uit_shotson': uit_shots,
        'thuis_shotsoff': thuis_shotsoff,
        'uit_shotsoff': uit_shotsoff,
        'thuis_crosses': thuis_crosses,
        'uit_crosses': uit_crosses,
        'thuis_corners': thuis_corners,
        'uit_corners': uit_corners,
        'home_pos': home_pos,
        'away_pos': away_pos,
    })

def Player(request, id):
    conn = sqlite3.connect('/Users/gerardvanderwel/Downloads/database.sqlite')
    c = conn.cursor()
    attr = c.execute("SELECT DISTINCT MAX(overall_rating), preferred_foot, attacking_work_rate, defensive_work_rate, crossing, finishing, heading_accuracy, short_passing, volleys, dribbling, curve, free_kick_accuracy, long_passing, ball_control, acceleration, sprint_speed, agility, reactions, balance, shot_power, jumping, stamina, strength, long_shots, aggression, interceptions, positioning, vision, penalties, marking, standing_tackle, sliding_tackle, gk_diving, gk_handling, gk_kicking, gk_positioning, gk_reflexes FROM Player_Attributes WHERE player_api_id=?", (id,))
    attr = attr.fetchall()
    print(attr)


    return render(request, 'Player.html', {
        'id': id,
        'attr': attr,
    })

def Home(request):
    return render(request, 'Home.html')



