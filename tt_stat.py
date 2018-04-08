# standard library
import os

# dash libs
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

# pydata stack
import pandas as pd
from sqlalchemy import create_engine

# set params
import sqlite3
# conn = create_engine(os.environ['DB_URI'])

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
        SELECT Date AS Дата, Opponent Соперник, Player_games Игры_игрока,
              Opponent_games Игры_соперника, Player_result Результат_игрока
        FROM results
        WHERE League='{0}'
        AND Year='{1}'
        AND Player='{2}'
        ORDER BY date ASC
        """.format(league, year, player)
    )
    total_results = fetch_data(results_query)
    return total_results


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
         html.H2('Результаты соревнований по настольному теннису')
    ]),

    # dropdown Grid
    html.Div([
        html.Div([
            # Select League
            html.Div([
                html.Div('Выберите лигу', className='four columns'),
                html.Div(dcc.Dropdown(id='league-selector', options=onLoad_league_options()),
                         className='eight columns')
            ]),

            # Select Year
            html.Div([
                html.Div('Выберите год', className='four columns'),
                html.Div(dcc.Dropdown(id='year-selector'), className='eight columns')
            ]),

            # Select Player
            html.Div([
                html.Div('Выберите игрока', className='four columns'),
                html.Div(dcc.Dropdown(id='player-selector'), className='eight columns')
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
                # columns=sorted(["Date", "Opponent", "Player_games", "Opponent_games", "Player_result"]),
                filterable=True,
                sortable=True,
                selected_row_indices=[],
                id='result-table'
            ),
        ),
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


# start Flask server
if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=1234
    )
