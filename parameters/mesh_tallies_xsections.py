import dash
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
from dash.dependencies import Output, State, Input

from app import app

layout = html.Div([

    # Title
    html.H2('Mesh, Tallies/Scoring, & Cross-Section Configuration',
            style={
                'position': 'relative',
                'top': '0px',
                'left': '10px',
                'font-family': 'Dosis',
                'display': 'inline',
                'font-size': '4.0rem',
                'color': 'rgb(76, 1, 3)'
            }), html.Br(),

    html.P("""
        In order to get the data we need from the simulation, we need to create one or multiple meshes in space and
        energy. The choice of the mesh(es) will be applied to the selected scores. A higher resolution in 
        any spatial dimension will result naturally result in higher quality results at the expense of computation time.
        Please select the type of mesh you would like to create from the dropdown then determine your desired selections 
        from the subsequent options that are displayed. The state of the mesh filter dropdown and the score/tally checklist
        will determine what mesh filters are applied to what scores. You may specify one spatial and one energy filter. 
        The filter dropdown will populate based on your latest energy and spatial mesh definitions.
           """),
    ########################################################################################################
    # Mesh
    html.Div([

        html.H2("Cross-sections"),
        html.H3('Number of Energy Groups'),
        html.Br(),
        dcc.Slider(
            id='energy-groups',
            min=0,
            max=100,
            step=1,
            value=5,
            marks={i: i for i in range(0, 100, 5)},
        ), html.Br(), html.Br(),

        html.Div([
            html.Label('Energy Start [eV]'),
            daq.NumericInput(
                id='energy-start',
                min=.001,
                max=20e6,
                value=0.001,
                size=193,
                # style=dict(float='left')
            )], style=dict(position='absolute', left=10)),

        dcc.RadioItems(id='energy-spacing', value='log', options=[
            {'label': 'Linear', 'value': 'lin'},
            {'label': 'Logarithmic', 'value': 'log'}
        ], style=dict(position='absolute', left='45%')),

        html.Div([
            html.Label('Energy End [eV]'),
            daq.NumericInput(
                id='energy-end',
                min=.001,
                max=20e6,
                value=20e6,
                size=193,

            )], style=dict(position='absolute', right=10)),

        html.Br(), html.Br(), html.Br(),

        dcc.Input(id='energy-filter-name', placeholder='Enter Name for Energy Filter'),
        html.Br(),
        html.Button('Save energy groups as energy filter', id='submit-energy-filter'),

        html.H3('Number of Delayed Groups'),
        dcc.Slider(
            id='delayed-groups',
            min=0,
            max=10,
            step=1,
            value=5,
            marks={i: i for i in range(0, 10, 1)},
        ), html.Br(),
        html.H3('Cross Section Library Options'),
        dcc.Dropdown(id='xsection-types', multi=True, options=[
            {'label': 'Total', 'value': 'total'},
            {'label': 'Transport', 'value': 'transport'},
            {'label': 'Nu Scatter Matrix', 'value': 'nu-scatter matrix'},
            {'label': 'Kappa Fission', 'value': 'kappa-fission'},
            {'label': 'Inverse Velocity', 'value': 'inverse-velocity'},
            {'label': 'Chi Prompt', 'value': 'chi-prompt'},
            {'label': 'Prompt Nu Fission', 'value': 'prompt-nu-fission'},
            {'label': 'Chi Delayed', 'value': 'chi-delayed'},
            {'label': 'Delayed Nu Fission', 'value': 'delayed-nu-fission'},
            {'label': 'Beta', 'value': 'beta'},
        ]),
        html.Br(),
        html.Button('Submit Cross-Section Configuration to Memory', id='xsection-button'),
        html.Br(), html.Br(),

        ########################################################################################################

        html.H3('Spatial Mesh'),
        html.Label('Mesh x-resolution'),
        dcc.Slider(id='mesh-x-slider',
                   min=1,
                   max=1000,
                   step=1,
                   value=100,
                   marks={i: i for i in range(0, 1000, 100)},
                   ),
        html.Br(),
        html.Label('Mesh y-resolution'),
        dcc.Slider(id='mesh-y-slider',
                   min=1,
                   max=1000,
                   step=1,
                   value=100,
                   marks={i: i for i in range(0, 1000, 100)},
                   ),
        html.Br(),
        html.Label('Mesh z-resolution'),
        dcc.Slider(id='mesh-z-slider',
                   min=1,
                   max=1000,
                   step=1,
                   value=100,
                   marks={i: i for i in range(0, 1000, 100)},
                   ),
        html.Br(), html.Br(),
        dcc.Input(id='mesh-name', value='Cartesian', placeholder='Enter Mesh Name', type="text"),
        html.Br(),
        html.Button('Submit Mesh as Spatial Filter', id='submit-mesh-button'),
    ]),

    ########################################################################################################
    # Tallies/Scores

    html.Div([

        html.H5('Select mesh filters for scoring'),
        dcc.Dropdown(id='mesh-filters-dropdown',
                     multi=True),

        html.Br(),
        html.H3('Desired Scores'),

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
        html.Button('Submit Desired Scores to Memory', id='submit-scores-btn', n_clicks=0),

        html.Div(style=dict(height=50))
    ]),
])


#######################################################################################################################
# Mesh Interface

@app.callback(
    Output('mesh-stores', 'data'),
    [Input('submit-mesh-button', 'n_clicks'),
     Input('submit-energy-filter', 'n_clicks')],
    [State('mesh-name', 'value'),

     State('energy-filter-name', 'value'),

     State('mesh-x-slider', 'value'),
     State('mesh-y-slider', 'value'),
     State('mesh-z-slider', 'value'),
     State('geometry-stores', 'data'),

     State('energy-groups', 'value'),
     State('energy-start', 'value'),
     State('energy-end', 'value'),
     State('energy-spacing', 'value'),

     State('mesh-stores', 'data')])
def mesh_creation(mesh_click, energy_click,
                  mesh_name, energy_name,
                  x_resolution, y_resolution, z_resolution, boundary_data,
                  energy_groups, energy_start, energy_end, energy_spacing,
                  mesh_data):
    mesh_data = mesh_data or {}

    trigger = dash.callback_context.triggered[0]

    if 'submit-mesh-button' in trigger['prop_id']:
        width = boundary_data['X-max'] - boundary_data['X-min']
        depth = boundary_data['Y-max'] - boundary_data['Y-min']
        height = boundary_data['Z-max'] - boundary_data['Z-min']

        mesh_data.update({'{}'.format(mesh_name): {'type': 'spatial',
                                                   'width': width,
                                                   'depth': depth,
                                                   'height': height,
                                                   'x-resolution': x_resolution,
                                                   'y-resolution': y_resolution,
                                                   'z-resolution': z_resolution}})

    if 'submit-energy-filter' in trigger['prop_id']:
        mesh_data.update({'{}'.format(energy_name): {'type': 'energy',
                                                     'energy-groups': energy_groups,
                                                     'energy-start': energy_start,
                                                     'energy-end': energy_end,
                                                     'energy-spacing': energy_spacing}
        })

    print(mesh_data)
    return mesh_data


# TODO: Not limiting to one energy/one spatial
@app.callback(
    Output('mesh-filters-dropdown', 'options'),
    [Input('mesh-stores', 'data')],
)
def populate_dropdown(mesh_data):
    mesh_options = []
    if mesh_data:
        for mesh_name in list(mesh_data.keys())[::-1]:
            num_energy_filters = 0
            num_spatial_filters = 0
            if mesh_data[mesh_name]['type'] == 'energy' and num_energy_filters < 1:
                mesh_options.append({'label': mesh_name, 'value': mesh_name})
                num_energy_filters += 1
            if mesh_data[mesh_name]['type'] == 'spatial' and num_spatial_filters < 1:
                mesh_options.append({'label': mesh_name, 'value': mesh_name})
                num_spatial_filters += 1

    return mesh_options


#######################################################################################################################
# Scores


@app.callback(
    Output('mesh-score-stores', 'data'),
    [Input('submit-scores-btn', 'n_clicks')],
    [State('mesh-filters-dropdown', 'value'),
     State('basic-checklist', 'values'),
     State('performance-checklist', 'values'),
     State('nu-other-checklist', 'values'),
     State('RR-checklist', 'values'),
     State('mesh-stores', 'data'),
     State('mesh-score-stores', 'data')]
)
def store_scores(click, mesh_filters, scores1, scores2, scores3, scores4, mesh_data, score_data):
    score_data = score_data or {}
    if click:
        scores = []
        [scores.extend(score) for score in [scores1, scores2, scores3, scores4]]
        score_data.update({'filters': [mesh_data[mesh_filter] for mesh_filter in mesh_filters],
                           'scores': scores})

    return score_data


#######################################################################################################################
# Cross-sections

@app.callback(
    Output('xsection-stores', 'data'),
    [Input('xsection-btn', 'n_clicks')],
    [State('energy-groups', 'value'),
     State('energy-start', 'value'),
     State('energy-end', 'value'),
     State('energy-spacing', 'value'),
     State('delayed-groups', 'value'),
     State('xsection-types', 'value'),
     State('xsection-stores', 'data')],
)
def build_xs_library(click, groups, start, end, spacing, delayed, types, xsection_data):
    xsection_data = xsection_data or {}
    if click:
        xsection_data.update({'energy-groups': groups,
                              'energy-start': start,
                              'energy-end': end,
                              'energy-spacing': spacing,
                              'delayed-groups': delayed,
                              'xsection-types': types})
    return xsection_data
