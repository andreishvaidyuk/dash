# standard library
import os

# dash libs
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff
import plotly.graph_objs as go

# pydata stack
import pandas as pd
from sqlalchemy import create_engine

# set params
import sqlite3
conn = create_engine(os.environ['DB_URI'])


#######################
# Data Analysis / Model
#######################

def fetch_data(q):
    result = pd.read_sql(
        sql=q,
        con=sqlite3.connect('tabletennis_stat')
    )
    return result

    #con = sqlite3.connect('soccer-stats.db?raw=true')
    #cur = con.cursor()
    #cur.execute("SELECT DISTINCT division FROM results")
    #data = cur.fetchall()
    #con.close()
    #return data


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


def get_match_results(league, year, player):
    results_query = (
        """
        SELECT Date, Player, Opponent, Player_games, Opponent_games, Player_result
        FROM results
        WHERE League='{0}'
        AND Year='{1}'
        AND Player='{2}'
        ORDER BY date ASC
        """.format(league, year, player)
    )
    match_results = fetch_data(results_query)
    return match_results


def calculate_year_summary(results):
    record = results.groupby(by=['Player_result'])['Player'].count()
    summary = pd.DataFrame(
        data={
            'Plays': record['W']+record['L'],
            'W': record['W'],
            'L': record['L']
        },
        columns=['Plays', 'W', 'L'],
        index=results['Player'].unique(),
    )
    return summary


# def draw_year_points_graph(results):
#     dates = results['Date']
#     points = results['points'].cumsum()
#
#     figure = go.Figure(
#         data=[
#             go.Scatter(x=dates, y=points, mode='lines+markets')
#         ],
#         layout=go.Layout(
#             title='Points Accumulation',
#             showlegend=False
#         )
#     )
#     return figure

#########################
# Dashboard Layout / View
#########################

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ])for i in range(min(len(dataframe), max_rows))]
    )


def onLoad_league_options():
    league_options = (
        [{'table': league, 'value': league}
         for league in get_league()]
    )
    return league_options


# Set up dashboard and create Layout
app = dash.Dash()
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

app.layout = html.Div([
    # Page Header
    html.Div([
        html.H1('Tabletennis results Viewer')
    ]),

    # dropdown Grid
    html.Div([
        html.Div([
            # Select League
            html.Div([
                html.Div('Select League', className='three columns'),
                html.Div(dcc.Dropdown(id='division-selector', options=onLoad_league_options()),
                         className='nine columns')
            ]),

            # Select Year
            html.Div([
                html.Div('Select Year', className='three columns'),
                html.Div(dcc.Dropdown(id='season-selector'), className='nine columns')
            ]),

            # Select Player
            html.Div([
                html.Div('Select Player', className='three columns'),
                html.Div(dcc.Dropdown(id='team-selector'), className='nine columns')
            ]),
        ], className='six columns'),

        # Empty
        html.Div(className='six columns'),
    ], className='twelve columns'),

    # Match results Grid
    html.Div([
        # Match Results Table
        html.Div(
            html.Table(id='match-results'),
            className='six columns'
        ),

        # Season Summary Table and Graph
        html.Div([
            # summary table
            dcc.Graph(id='season-summary'),

            # graph
            dcc.Graph(id='season-graph')
            # style = {},
        ], className='six columns')
    ]),
])


#############################################
# Interaction Between Components / Controller
#############################################

# Load Years
@app.callback(
    Output(component_id='season-selector', component_property='options'),
    [
        Input(component_id='division-selector', component_property='value')
    ]
)
def populate_year_selector(league):
    years = get_year(league)
    return [
        {'label': year, 'value': year}
        for year in years
    ]


# Load Player
@app.callback(
    Output(component_id='team-selector', component_property='options'),
    [
        Input(component_id='division-selector', component_property='value'),
        Input(component_id='season-selector', component_property='value'),
    ]
)
def populate_player_selector(league, year):
    players = get_players(league, year)
    return [
        {'label': player, 'value': player}
        for player in players
    ]


# Load Match Results
@app.callback(
    Output(component_id='match-results', component_property='children'),
    [
        Input(component_id='division-selector', component_property='value'),
        Input(component_id='season-selector', component_property='value'),
        Input(component_id='team-selector', component_property='value')
    ]
)
def load_match_results(league, year, player):
    results = get_match_results(league, year, player)
    return generate_table(results, max_rows=50)


# Update Season Summary Table
@app.callback(
    Output(component_id='season-summary', component_property='figure'),
    [
        Input(component_id='division-selector', component_property='value'),
        Input(component_id='season-selector', component_property='value'),
        Input(component_id='team-selector', component_property='value')
    ]
)
def load_season_summary(league, year, player):
    results = get_match_results(league, year, player)
    table = []
    if len(results) > 0:
        summary = calculate_year_summary(results)
        table = ff.create_table(summary)

    return table


# Update Season Point Graph
# @app.callback(
#     Output(component_id='season-graph', component_property='figure'),
#     [
#         Input(component_id='division-selector', component_property='value'),
#         Input(component_id='season-selector', component_property='value'),
#         Input(component_id='team-selector', component_property='value')
#     ]
# )
# # def load_season_point_graph(league, year, player):
#     results = get_match_results(league, year, player)
#
#     figure = []
#     if len(results) > 0:
#         figure = draw_year_points_graph(results)
#
#     return figure

# start Flask server
if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050
    )
