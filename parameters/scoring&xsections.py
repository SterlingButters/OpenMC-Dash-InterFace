import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, State, Input

import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([

    # Title
    html.H2('Tallies/Scoring & Cross-Section Configuration',
            style={
                'position': 'relative',
                'top': '0px',
                'left': '10px',
                'font-family': 'Dosis',
                'display': 'inline',
                'font-size': '4.0rem',
                'color': '#4D637F'
            }), html.Br(),

    dcc.Store(id='score-stores', storage_type='session'),

    html.Div([
        html.H5('Select mesh filters for scoring'),
        dcc.Dropdown(id='mesh-filters-dropdown',
                     multi=True),

        html.Label('Desired Scores'),

        html.Div([
            html.Div([
                html.H5('Basic Metrics'),
                dcc.Checklist(
                    id='basic-checklist',
                    options=[
                        {'label': 'Flux', 'value': 'flux'},
                        {'label': 'Absorption', 'value': 'absorption'},
                        {'label': 'Elastic', 'value': 'elastic'},
                        {'label': 'Fission', 'value': 'fission'},
                        {'label': 'Total', 'value': 'total'},
                        {'label': 'Scatter', 'value': 'scatter'},
                    ],
                    values=['flux', 'absorption', 'elastic', 'fission', 'total', 'scatter'],
                    className='',  # TODO: Custom Style
                    labelStyle={'display': 'block'}
                ), html.Br(),

                html.H5('Performance Metrics'),
                dcc.Checklist(
                    id='performance-checklist',
                    options=[
                        {'label': 'Current', 'value': 'current'},
                        {'label': 'Events', 'value': 'events'},
                        {'label': 'Inverse Velocity', 'value': 'inverse-velocity'},
                        {'label': 'Kappa Fission', 'value': 'kappa-fission'},
                        {'label': 'Q Prompt Fission', 'value': 'fission-q-prompt'},
                        {'label': 'Q Recoverable Fission', 'value': 'fission-q-recoverable'},
                        {'label': 'Decay Rate', 'value': 'decay-rate'},
                    ],
                    values=['current', 'events', 'decay-rate', 'fission-q-recoverable'],
                    className='',  # TODO: Custom Style
                    labelStyle={'display': 'block'}
                )
            ],
                style=dict(
                    width='30%',
                    display='table-cell',
                    verticalAlign="top",
                ),
            ),
            html.Div([
                html.H5('Misc Metrics'),
                dcc.Checklist(
                    id='nu-other-checklist',
                    options=[
                        {'label': 'Nu Delayed Fission', 'value': 'delayed-nu-fission'},
                        {'label': 'Nu Prompt Fission', 'value': 'prompt-nu-fission'},
                        {'label': 'Nu Fission', 'value': 'nu-fission'},
                        {'label': 'Nu Scatter', 'value': 'nu-scatter'},
                        {'label': 'Nu Scatter N', 'value': 'nu-scatter-N'},
                        {'label': 'Nu Scatter PN', 'value': 'nu-scatter-PN'},
                        {'label': 'Nu Scatter YN', 'value': 'nu-scatter-YN'},

                        {'label': 'scatter-N', 'value': 'scatter-N'},
                        {'label': 'scatter-PN', 'value': 'scatter-PN'},
                        {'label': 'scatter-YN', 'value': 'scatter-YN'},
                        {'label': 'Total-YN', 'value': 'total-YN'},
                        {'label': 'Flux-YN  ', 'value': 'flux-YN'},
                    ],
                    values=['delayed-nu-fission', 'prompt-nu-fission'],
                    className='',  # TODO: Custom Style
                    labelStyle={'display': 'block'}
                )
            ],
                style=dict(
                    width='30%',
                    display='table-cell',
                    verticalAlign="top",
                ),
            ),

            html.Div([
                html.H5('Comprehensive Reaction Rates'),
                dcc.Checklist(
                    id='RR-checklist',
                    options=[
                        {'label': '(n,2nd)', 'value': '(n,2nd)'},
                        {'label': '(n,2n)', 'value': '(n,2n)'},
                        {'label': '(n,3n)', 'value': '(n,3n)'},
                        {'label': '(n,na)', 'value': '(n,na)'},
                        {'label': '(n,n3a)', 'value': '(n,n3a)'},
                        {'label': '(n,2na)', 'value': '(n,2na)'},
                        {'label': '(n,3na)', 'value': '(n,3na)'},
                        {'label': '(n,np)', 'value': '(n,np)'},
                        {'label': '(n,n2a)', 'value': '(n,n2a)'},
                        {'label': '(n,2n2a)', 'value': '(n,2n2a)'},
                        {'label': '(n,nd)', 'value': '(n,nd)'},
                        {'label': '(n,nt)', 'value': '(n,nt)'},
                        {'label': '(n,nHe-3)', 'value': '(n,nHe-3)'},
                        {'label': '(n,nd2a)', 'value': '(n,nd2a)'},
                        {'label': '(n,nt2a)', 'value': '(n,nt2a)'},
                        {'label': '(n,4n)', 'value': '(n,4n)'},
                        {'label': '(n,2np)', 'value': '(n,2np)'},
                        {'label': '(n,3np)', 'value': '(n,3np)'},
                        {'label': '(n,n2p)', 'value': '(n,n2p)'},
                        {'label': '(n,n*X*)', 'value': '(n,n*X*)'},
                        {'label': '(n,nc)', 'value': '(n,nc)'},
                        {'label': '(n,gamma)', 'value': '(n,gamma)'},
                        {'label': '(n,p)', 'value': '(n,p)'},
                        {'label': '(n,d)', 'value': '(n,d)'},
                        {'label': '(n,t)', 'value': '(n,t)'},
                        {'label': '(n,3He)', 'value': '(n,3He)'},
                        {'label': '(n,a)', 'value': '(n,a)'},
                        {'label': '(n,2a)', 'value': '(n,2a)'},
                        {'label': '(n,3a)', 'value': '(n,3a)'},
                        {'label': '(n,2p)', 'value': '(n,2p)'},
                        {'label': '(n,pa)', 'value': '(n,pa)'},
                        {'label': '(n,t2a)', 'value': '(n,t2a)'},
                        {'label': '(n,d2a)', 'value': '(n,d2a)'},
                        {'label': '(n,pd)', 'value': '(n,pd)'},
                        {'label': '(n,pt)', 'value': '(n,pt)'},
                        {'label': '(n,da)', 'value': '(n,da)'},
                        # Integer
                    ],
                    values=[],
                    className='',  # TODO: Custom Style
                    labelStyle={'display': 'block'}
                )
            ],
                style=dict(
                    width='30%',
                    display='table-cell',
                    verticalAlign="top",
                ),
            )

        ], style=dict(
            width='100%',
            display='table',
        ),
        ),
        html.Button('Submit Desired Scores to Memory', id='submit-scores-btn', n_clicks=0)

        ########################################################################################################
        html.Label('Number of Energy Groups'),
        html.Br(),
        dcc.Slider(
            id='energy-group-input',
            min=0,
            max=100,
            step=1,
            value=5,
            marks={i: i for i in range(0, 100, 5)},
        ),
        html.Br(),
        html.Label('Select mesh to apply to cross-section calculations'),
        html.A(id='cross-section-message'),

    ]),
])


############################################################################################################


@app.callback(
    Output('score-stores', 'data'),
    [Input('submit-scores-btn', 'n_clicks')],
    [State('basic-checklist', 'values'),
     State('performance-checklist', 'values'),
     State('nu-other-checklist', 'values'),
     State('RR-checklist', 'values')]
)
def store_scores(click, scores1, scores2, scores3, scores4):
    scores = []
    if click:
        [scores.extend(score) for score in [scores1, scores2, scores3, scores4]]
        print(scores)
        return scores


# TODO: import mesh into function
# @app.callback(
#     Output('cross-section-message', 'children'),
#     [Input('energy-group-input', 'value'),
#      Input('mesh-dropdown', 'value')],
# )
# def build_xs_library(groups, meshes):
#     energy_groups = openmc.mgxs.EnergyGroups()
#     # TODO: Make sure the groups+1 is accurate
#     energy_groups.group_edges = np.logspace(-3, 7.3, groups + 1)
#
#     # Instantiate a 1-group EnergyGroups object
#     # one_group = openmc.mgxs.EnergyGroups()
#     # one_group.group_edges = np.array([energy_groups.group_edges[0], energy_groups.group_edges[-1]])
#
#     mgxs_lib.energy_groups = energy_groups
#     # TODO: Get user-specified delayed groups
#     mgxs_lib.num_delayed_groups = 6
#
#     # Specify multi-group cross section types to compute
#     mgxs_lib.mgxs_types = ['total', 'transport', 'nu-scatter matrix', 'kappa-fission', 'inverse-velocity', 'chi-prompt',
#                            'prompt-nu-fission', 'chi-delayed', 'delayed-nu-fission', 'beta']
#     # Specify a "mesh" domain type for the cross section tally filters
#     mgxs_lib.domain_type = 'mesh'
#
#     # Specify the mesh domain(s) over which to compute multi-group cross sections
#     for mesh in meshes:
#         mgxs_lib.domains.append(mesh)
#
#     # Construct all tallies needed for the multi-group cross section library
#     mgxs_lib.build_library()
#
#     message = 'Cross-section library built'
#
#     return message


if __name__ == '__main__':
    app.run_server(debug=True)
