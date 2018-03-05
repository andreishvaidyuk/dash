import pandas as pd

import plotly.graph_objs as go

import sqlite3

#######################
# Data Analysis / Model
#######################


def fetch_data(q):
    result = pd.read_sql(
        sql=q,
        con=sqlite3.connect('tabletennis_stat')
    )
    return result


def get_league():
    league_query = (
        """
        SELECT DISTINCT League
        FROM results
        """
    )
    leagues = fetch_data(league_query)
    leagues = list(leagues['League'].sort_values(ascending=True))
    return leagues


def get_year(league):
    year_query = (
        """SELECT DISTINCT Year
        FROM results
        WHERE League='{0}'
        """.format(league)
    )
    years = fetch_data(year_query)
    years = list(years['Year'].sort_values(ascending=True))
    return years


def get_players(league, year):
    players_query = (
        """
        SELECT DISTINCT Player
        FROM results
        WHERE League='{0}'
        AND Year='{1}'
        """.format(league, year)
    )

    players = fetch_data(players_query)
    players = list(players['Player'].sort_values(ascending=True))
    return players


def get_total_results(league, year, player):
    results_query = (
        """
        SELECT Date, Opponent, Player_games, Opponent_games, Player_result
        FROM results
        WHERE League='{0}'
        AND Year='{1}'
        AND Player='{2}'
        ORDER BY date ASC
        """.format(league, year, player)
    )
    total_results = fetch_data(results_query)
    return total_results


def draw_year_points_graph(results):
    dates = results['Date']
    df = pd.DataFrame(results)
    points = df[(df.Player_result == 'W')].count()
    figure = go.Figure(
        data=[
            go.Scatter(x=dates, y=points, mode='markets')
        ],
        layout=go.Layout(
            title='Wins',
            showlegend=False
        )
    )
    return figure
