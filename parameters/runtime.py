import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, State, Input

import plotly.graph_objs as go

import openmc
import openmc.model
import openmc.mgxs

import numpy as np
import time
import io
import re
from glob import glob
import os
from contextlib import redirect_stdout


app = dash.Dash()
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([

    # Title
    html.H2('Runtime/Setting Configuration',
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
        html.Label('Total/Inactive Batches for Simulation'),
        dcc.RangeSlider(
            id='total-inactive-batches',
            min=0,
            max=100,
            value=[5, 10],
            marks={i: i for i in range(0, 100, 5)},
            included=False,
            pushable=5),

        html.Br(),
        html.Label('Number of Generations per Batch in Simulation'),
        dcc.Slider(
            id='generations-per-batch',
            min=0,
            max=100,
            step=1,
            value=10,
            marks={i: i for i in range(0, 100, 5)}
        ),
        html.Br(),
        html.Label('Number of Particles in Simulation'),
        dcc.Slider(
            id='particles-input',
            min=0,
            max=10000,
            step=1,
            value=500,
            marks={i: i for i in range(0, 10000, 500)}
        ),
        html.A(id='settings-message'),
        html.Br(),
    ]),
])

############################################################################################################
# Settings Interface

# restore_object('model').settings.confidence_intervals = False
# restore_object('model').settings.cutoff =
# restore_object('model').settings.eigenvalue
# restore_object('model').settings.energy_grid =
# restore_object('model').settings.entropy
# restore_object('model').settings.fixed_source
# log_grid_bins # Default: 8000
# natural_elements = ENDF/B-VII.0 or JENDL-4.0
# restore_object('model').settings.no_reduce = True
# restore_object('model').settings.output.cross_sections = False
# restore_object('model').settings.output.summary = False
# restore_object('model').settings.output.tallies = True
# restore_object('model').settings.ptables = True
# restore_object('model').settings.run_cmfd = False
# restore_object('model').settings.seed = 1
# restore_object('model').settings.source
# restore_object('model').settings.state_point
# restore_object('model').settings.source_point
# restore_object('model').settings.survival_biasing
# restore_object('model').settings.threads
# restore_object('model').settings.trace
# restore_object('model').settings.track
# restore_object('model').settings.trigger
# restore_object('model').settings.uniform_fs
# restore_object('model').settings.verbosity = 10
# Resonance Scattering


@app.callback(
    Output('settings-message', 'children'),
    [State('total-inactive-batches', 'value'),
     State('generations-per-batch', 'value'),
     State('particles-input', 'value')]
)
def define_settings(total_batches, generations_per_batch, particles):
    # Make sure this works
    cross_sections = '/cross-sections/cross_sections.xml'

    return


############################################################################################################

@app.callback(
    Output(component_id='console-output', component_property='value'),
    [Input(component_id='xml-button', component_property='n_clicks')], )
def run_model(run_click):
    if int(run_click) > 0:

        xml_files = glob('./xml-files/*.xml')
        print(xml_files)

        pass_test = False
        while not pass_test:
            bool_array = []
            for file in range(len(xml_files)):
                exists = os.path.exists(xml_files[file])
                if exists:
                    bool_array.append(exists)

            if np.array(bool_array).all():
                pass_test = True
                print('All files exist')

            time.sleep(1)

        output = io.StringIO()
        with redirect_stdout(output):
            openmc.run()

        run_click = 0

        return output.getvalue()


#######################################################################################################################
# Load XML from File
@app.callback(
    Output(component_id='materials-xml', component_property='value'),
    [Input(component_id='load-materials', component_property='n_clicks')],
)
def show_material_xml_contents(run_click):
    if run_click > 0:
        filename = 'materials.xml'
        contents = open(filename).read()
        return contents


@app.callback(
    Output(component_id='geometry-xml', component_property='value'),
    [Input(component_id='load-geometry', component_property='n_clicks')],
)
def show_material_xml_contents(run_click):
    if run_click > 0:
        filename = 'geometry.xml'
        contents = open(filename).read()
        return contents


@app.callback(
    Output(component_id='tallies-xml', component_property='value'),
    [Input(component_id='load-tallies', component_property='n_clicks')],
)
def show_material_xml_contents(run_click):
    if run_click > 0:
        filename = 'tallies.xml'
        contents = open(filename).read()
        return contents


@app.callback(
    Output(component_id='settings-xml', component_property='value'),
    [Input(component_id='load-settings', component_property='n_clicks')],
)
def show_material_xml_contents(run_click):
    if run_click > 0:
        filename = 'settings.xml'
        contents = open(filename).read()
        return contents


@app.callback(
    Output(component_id='plots-xml', component_property='value'),
    [Input(component_id='load-plots', component_property='n_clicks')],
)
def show_material_xml_contents(run_click):
    if run_click > 0:
        filename = 'plots.xml'
        contents = open(filename).read()
        return contents


#######################################################################################################################
# Write XML to File
@app.callback(
    Output(component_id='material-placeholder', component_property='children'),
    [Input(component_id='write-materials', component_property='n_clicks')],
    [State(component_id='materials-xml', component_property='value')],
)
def write_material_xml_contents(write_click, contents):
    if write_click > 0:
        filename = 'materials.xml'
        file = open(filename, "w+")
        file.write(contents)
        file.close()


@app.callback(
    Output(component_id='geometry-placeholder', component_property='children'),
    [Input(component_id='write-geometry', component_property='n_clicks')],
    [State(component_id='geometry-xml', component_property='value')],
)
def write_material_xml_contents(write_click, contents):
    if write_click > 0:
        filename = 'geometry.xml'
        file = open(filename, "w+")
        file.write(contents)
        file.close()


@app.callback(
    Output(component_id='tallies-placeholder', component_property='children'),
    [Input(component_id='write-tallies', component_property='n_clicks')],
    [State(component_id='tallies-xml', component_property='value')],
)
def write_material_xml_contents(write_click, contents):
    if write_click > 0:
        filename = 'tallies.xml'
        file = open(filename, "w+")
        file.write(contents)
        file.close()


@app.callback(
    Output(component_id='settings-placeholder', component_property='children'),
    [Input(component_id='write-settings', component_property='n_clicks')],
    [State(component_id='settings-xml', component_property='value')],
)
def write_material_xml_contents(write_click, contents):
    if write_click > 0:
        filename = 'settings.xml'
        file = open(filename, "w+")
        file.write(contents)
        file.close()


@app.callback(
    Output(component_id='plots-placeholder', component_property='children'),
    [Input(component_id='write-plots', component_property='n_clicks')],
    [State(component_id='plots-xml', component_property='value')],
)
def write_material_xml_contents(write_click, contents):
    if write_click > 0:
        filename = 'plots.xml'
        file = open(filename, "w+")
        file.write(contents)
        file.close()


#######################################################################################################################
@app.callback(
    Output(component_id='score-graph-dropdown', component_property='options'),
    [Input(component_id='scores-checklist', component_property='values')],
)
def disable_unscored_dropdown(scores):
    return [{'label': score.title(), 'value': score, 'disabled': False} for score in scores]


#######################################################################################################################


@app.callback(
    Output(component_id='graph', component_property='figure'),
    [Input(component_id='score-graph-dropdown', component_property='value')],
)
def statepoint_evaluation(desired_score, ):
    sp = openmc.StatePoint(filename=str(*glob('statepoint*')))

    # Get k_effs for each generation
    k_effs = sp.k_generation

    # Extract the current tally separately
    if desired_score == 'current':
        tally = sp.get_tally(scores=[desired_score])
        goal = tally.get_slice(scores=[desired_score])

    else:
        tally = sp.get_tally(scores=[desired_score])
        goal = tally.get_slice(scores=[desired_score])

    # Initialize MGXS Library with OpenMC statepoint data
    # xs_lib.load_from_statepoint(sp)

    dims = (10, 17, 17)
    goal_array = goal.get_values().reshape(dims)

    ##############################################################################################
    # data = [go.Surface(z=goal_array[0],
    #                    # zmax=c_max,
    #                    # zmin=0,
    #                    colorscale='Viridis',
    #                    )]
    ##############################################################################################

    maxes = []
    for m in range(len(goal_array)):
        c_max = np.amax(np.array(goal_array[m]))
        maxes.append(c_max)
    c_max = np.max(np.array(maxes))

    # Instantiate Data
    data = [go.Surface(z=goal_array[0],
                       zmax=c_max,
                       zmin=0,
                       colorscale='Viridis',
                       )]

    ##############################################

    # Instantiate Frames
    frames = []
    steps = []
    for k in range(len(goal_array)):
        frame_data = go.Surface(z=goal_array[k])
        frame = dict(data=[frame_data], name='Axial Step {}'.format(k))
        frames.append(frame)

        slider_step = dict(args=[
            [str(goal_array[k])],
            dict(frame=dict(duration=0, redraw=False),
                 mode='immediate',
                 transition={'duration': 0})
        ],
            label='{} cm'.format(goal_array[k]),
            method='animate')
        steps.append(slider_step)

    ##################################################################

    # Slider Control
    sliders_dict = dict(active=0,  # Starting Position
                        yanchor='top',
                        xanchor='left',
                        currentvalue=dict(
                            font={'size': 20},
                            prefix='Axial Step:',
                            visible=True,
                            xanchor='right'
                        ),
                        # Transition for slider button
                        transition=dict(duration=500,
                                        easing='cubic-in-out'),
                        pad={'b': 10, 't': 50},
                        len=.9,
                        x=0.1,
                        y=0,
                        steps=steps
                        )

    ##################################################################

    # Layout
    layout = dict(title='Test',
                  hovermode='closest',
                  width=1500,
                  height=1000,
                  scene=dict(
                      zaxis=dict(range=[.01, c_max])),
                  updatemenus=[dict(type='buttons',

                                    buttons=[dict(args=[None,
                                                        dict(frame=dict(duration=500,
                                                                        redraw=False),
                                                             fromcurrent=True,
                                                             transition=dict(duration=100,
                                                                             easing='quadratic-in-out'))],
                                                  label=u'Play',
                                                  method=u'animate'
                                                  ),

                                             # [] around "None" are important!
                                             dict(args=[[None], dict(frame=dict(duration=0,
                                                                                redraw=False),
                                                                     mode='immediate',
                                                                     transition=dict(duration=0))],
                                                  label='Pause',
                                                  method='animate'
                                                  )
                                             ],

                                    # Play Pause Button Location & Properties
                                    direction='left',
                                    pad={'r': 10, 't': 87},
                                    showactive=True,
                                    x=0.1,
                                    xanchor='right',
                                    y=0,
                                    yanchor='top'
                                    )],

                  slider=dict(args=[
                      'slider.value', {
                          'duration': 1000,
                          'ease': 'cubic-in-out'
                      }
                  ],
                      # initialValue=burnup[0],           # ???
                      plotlycommand='animate',
                      # values=burnup,                    # ???
                      visible=True
                  ),
                  sliders=[sliders_dict]
                  )

    ##################################################################

    figure = dict(data=data, layout=layout, frames=frames)

    ###################################
    # trace = go.Scatter(
    #     x=np.arange(len(k_effs)),
    #     y=k_effs,
    #     mode='line'
    # )
    # data = [trace]
    # layout = dict(title='K-effective vs Iteration')
    # figure = dict(data=data, layout=layout)
    ###################################

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
