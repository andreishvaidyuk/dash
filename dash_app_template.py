# standard library
import os

# dash libs
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff
import plotly.graph_objs as go
import dash_table_experiments as dt
import plotly


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

#########################
# Dashboard Layout / View
#########################

def onLoad_league_options():
    league_options = (
        [{'label': league, 'value': league}
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
         html.H1('Tabletennis results')
    ]),

    # dropdown Grid
    html.Div([
        html.Div([
            # Select League
            html.Div([
                html.Div('Select League', className='three columns'),
                html.Div(dcc.Dropdown(id='league-selector', options=onLoad_league_options()),
                         className='nine columns')
            ]),

            # Select Year
            html.Div([
                html.Div('Select Year', className='three columns'),
                html.Div(dcc.Dropdown(id='year-selector'), className='nine columns')
            ]),

            # Select Player
            html.Div([
                html.Div('Select Player', className='three columns'),
                html.Div(dcc.Dropdown(id='player-selector'), className='nine columns')
            ]),
        ], className='six columns'),

        # Empty
        html.Div(className='six columns'),
    ], className='twelve columns'),

    html.Div([
        # Total Results Table
        html.Div(
            dt.DataTable(
                rows=[{}],
                filterable=True,
                sortable=True,
                selected_row_indices=[],
                id='result-table'
            ),
        ),

        # Player Results Graph
        html.Div([
            dcc.Graph(id='player-results-graph')
        ], className='three columns')
    ]),
])

#############################################
# Interaction Between Components / Controller
#############################################

# Load Years
@app.callback(
    Output(component_id='year-selector', component_property='options'),
    [
        Input(component_id='league-selector', component_property='value')
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
    Output(component_id='player-selector', component_property='options'),
    [
        Input(component_id='league-selector', component_property='value'),
        Input(component_id='year-selector', component_property='value'),
    ]
)
def populate_player_selector(league, year):
    players = get_players(league, year)
    return [
        {'label': player, 'value': player}
        for player in players
    ]


# # Load Total Results
@app.callback(
    Output(component_id='result-table', component_property='rows'),
    [
        Input(component_id='league-selector', component_property='value'),
        Input(component_id='year-selector', component_property='value'),
        Input(component_id='player-selector', component_property='value')
    ]
)
def load_total_results(league, year, player):
    results = get_total_results(league, year, player)
    return results.to_dict('records')


# Update Player Results Graph
@app.callback(
    Output(component_id='player-results-graph', component_property='figure'),
    [
        Input(component_id='league-selector', component_property='value'),
        Input(component_id='year-selector', component_property='value'),
        Input(component_id='player-selector', component_property='value')
    ]
)
def load_season_point_graph(league, year, player):
    results = get_total_results(league, year, player)

    figure = []
    if len(results) > 0:
        figure = draw_year_points_graph(results)

    return figure


# start Flask server
if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050
    )
