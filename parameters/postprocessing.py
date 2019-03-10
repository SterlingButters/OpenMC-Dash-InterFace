from glob import glob

import dash_html_components as html
import dash_core_components as dcc
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
                'color': '#4D637F'
            }),
    html.Br(),
    dcc.Dropdown(id='score-graph-dropdown'),
    html.Div(id='surface-graph')
])


@app.callback(
    Output(component_id='surface-graph', component_property='figure'),
    [Input(component_id='score-graph-dropdown', component_property='value')],
)
def statepoint_evaluation(desired_score):
    if str(*glob('statepoint*')):
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

        return dcc.Graph(figure=figure)

    else:
        return html.P('Statepoint file not available')
