from glob import glob

import dash_core_components as dcc
import dash_html_components as html
import dash_resumable_upload
import numpy as np
import openmc
import plotly.graph_objs as go
from dash.dependencies import Output, Input

from app import app

layout = html.Div([
    html.H2('Post Processing',
            style={
                'position': 'relative',
                'top': '0px',
                'left': '10px',
                'font-family': 'Dosis',
                'display': 'inline',
                'font-size': '4.0rem',
                'color': 'rgb(76, 1, 3)'
            }),
    html.Br(),
    html.P("""
    Now for the most exciting portion: a visual representation of our model and the specifications that were created.
    If you would like to merely upload a statepoint and summary file, you may do so with the file uploader. Otherwise,
    the statepoint file generated from the simulation conducted previously will be used. 
       """),
    dash_resumable_upload.Upload(
        id='upload',
        maxFiles=1,
        maxFileSize=1024 * 1024 * 10000,  # 100 MB
        service="/upload_resumable",
        textLabel="Drag and Drop Here to upload!",
        startButton=False,
        activeStyle={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        defaultStyle={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        completeStyle={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allowed arguments: activeStyle, cancelButton, chunkSize, className, completeClass, completeStyle, completedMessage, defaultStyle, disableDragAndDrop, disabledClass, fileNames, filetypes, hoveredClass, id, maxFileSize, maxFiles, pauseButton, pausedClass, service, simultaneousUploads, startButton, textLabel, uploadingClass
    ),
    html.Div(id='upload-status'),

    html.Br(),
    dcc.Dropdown(id='score-graph-dropdown'),
    html.Div(id='k-eff-vs-iter'),
    html.Button('Graph k-eff', id='graph-btn', n_clicks=0), html.Br(),
    html.Button('Search for Statepoint', id='check-file', n_clicks=0),
    html.Div(id='surface-graph')
])


@app.callback(Output('upload-status', 'children'),
              [Input('upload', 'fileNames')])
def display_files(fileNames):
    if fileNames is not None:
        return html.P("Uploaded Files: {}".format(fileNames))
    return html.P('No Files Uploaded Yet')


@app.callback(
    Output('k-eff-vs-iter', 'children'),
    [Input('graph-btn', 'n_clicks')]
)
def graph_k_eff(click):
    if click:
        if str(*glob('statepoint*')):
            sp = openmc.StatePoint(filename=str(*glob('statepoint*')))
            # Get k_effs for each generation
            k_effs = sp.k_generation

            trace = go.Scatter(
                x=np.arange(len(k_effs)),
                y=k_effs,
                mode='lines'
            )
            data = [trace]
            layout = dict(title='K-effective vs Iteration')
            figure = dict(data=data, layout=layout)
            return dcc.Graph(figure=figure)


@app.callback(
    Output('score-graph-dropdown', 'options'),
    [Input('check-file', 'n_clicks')]
)
def pop_drop(click):
    options = []

    if str(*glob('statepoint*')):
        sp = openmc.StatePoint(filename=str(*glob('statepoint*')))

        # Get k_effs for each generation
        k_effs = sp.k_generation

        # Extract the current tally separately
        tally = sp.get_tally()
        available_scores = tally._scores

        for score in available_scores:
            options.append({'label': score, 'value': score})

        return options


@app.callback(
    Output('surface-graph', 'children'),
    [Input('score-graph-dropdown', 'value')]
)
def statepoint_evaluation(desired_score):
    if desired_score and str(*glob('statepoint*')):
        sp = openmc.StatePoint(filename=str(*glob('statepoint*')))

        # Extract the current tally separately
        tally = sp.get_tally()
        if desired_score == 'current':
            goal = tally.get_slice(scores=[desired_score])

        else:
            goal = tally.get_slice(scores=[desired_score])

        # Initialize MGXS Library with OpenMC statepoint data
        # xs_lib.load_from_statepoint(sp)

        print(sp.meshes)

        goal_array = goal.get_values().reshape(sp.meshes[2]._dimension)

        maxes = []
        for m in range(len(goal_array)):
            c_max = np.amax(np.array(goal_array[m]))
            maxes.append(c_max)
        c_max = np.max(np.array(maxes))

        # Instantiate Data
        data = []
        for i in range(0, len(goal_array), 10):
            data.append(go.Surface(z=np.full(fill_value=i, shape=np.shape(goal_array[i])),
                                   colorscale='Viridis',
                                   surfacecolor=goal_array[i],
                                   cmax=c_max
                                   ))

        layout = dict(title='Visualization',
                      hovermode='closest',
                      width=1500,
                      height=1000,)

        figure = dict(data=data, layout=layout, )  # frames=frames)

        return dcc.Graph(figure=figure)

    else:
        return html.P('Statepoint file not available')
