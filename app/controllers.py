import dash

from dash.dependencies import Input, Output

#############################################
# Interaction Between Components / Controller
#############################################

app = dash.Dash()


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
