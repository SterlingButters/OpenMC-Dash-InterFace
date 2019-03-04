import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, State, Input

import plotly.graph_objs as go

import openmc
import openmc.model
import openmc.mgxs

import numpy as np
import re
import pickle
import redis

app = dash.Dash()
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([

    # Title
    html.H2('Tallies/Scoring Configuration',
            style={
                'position': 'relative',
                'top': '0px',
                'left': '10px',
                'font-family': 'Dosis',
                'display': 'inline',
                'font-size': '4.0rem',
                'color': '#4D637F'
            }), html.Br(),

    html.Div([
        html.Button('Configure Scoring', id='config-scores-button', n_clicks=0),
        html.Div(id='scores-config-container'),
    ]),
])
#######################################################################################################################
# Initialize model & redisworks for memory sharing between callbacks
r = redis.StrictRedis(host='localhost', port=6379, db=0)
r.flushall()


def store_object(key, obj):
    var = pickle.dumps(obj)
    r.set(key, var)


def restore_object(key):
    obj = pickle.loads(r.get(key))
    return obj


store_object('model', openmc.model.Model())

############################################################################################################
# Tallies Interface
restore_object('model').tallies = openmc.Tallies()


@app.callback(
    Output('scores-config-container', 'children'),
    [Input('config-scores-button', 'n_clicks')], )
def invoke_scores_options(n_clicks):
    if n_clicks > 0:
        options = html.Div([
            html.Label('Select mesh filters for scoring'),
            dcc.Dropdown(id='mesh-filters-dropdown',
                         multi=True),
            html.Label('Desired Scores'),
            # TODO: Add the rest of the scores
            dcc.Checklist(
                id='scores-checklist',
                options=[
                    {'label': 'Flux  ', 'value': 'flux'},

                    {'label': 'Absorption  ', 'value': 'absorption'},
                    {'label': 'Elastic   ', 'value': 'elastic'},
                    {'label': 'Fission  ', 'value': 'fission'},
                    {'label': 'Scatter  ', 'value': 'scatter'},
                    {'label': 'Total  ', 'value': 'total'},

                    {'label': 'Current  ', 'value': 'current'},
                    {'label': 'Decay Rate  ', 'value': 'decay-rate'},

                ],
                values=['flux']),
            html.A(id='scores-message')
        ])

        return options


@app.callback(
    Output('mesh-filters-dropdown', 'options'))
def populate_mesh_filter_dropdown():
    options = []
    for mesh_filter in range(len(mesh_filters_list)):
        # TODO: Make sure this is correct
        options.append({'label': mesh_filters_list[mesh_filter].name, 'value': mesh_filter})

    return options


# TODO: Import mesh_filter/mgxs_lib to function
@app.callback(
    Output('scores-message', 'children'),
    [Input('scores-checklist', 'value'),
     Input('mesh-filters-dropdown', 'value')]
)
def create_tallies(scores, mesh_filters):
    mgxs_lib.add_to_tallies_file(restore_object('model').tallies, merge=True)

    # TODO: Allow for user specified combination of scores and mesh filters; for now just do everything
    for score in scores:
        for filter in range(len(mesh_filters)):
            tally = openmc.Tally(name=score)
            tally.filters = [mesh_filters[filter]]
            tally.scores = [score]

            # Add tally to the tallies file
            restore_object('model').tallies.append(tally)

    # message =
    return


if __name__ == '__main__':
    app.run_server(debug=True)
