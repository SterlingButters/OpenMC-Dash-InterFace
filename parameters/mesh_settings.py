# TODO: Mesh/Scoring/Settings in one
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html

from app import app

layout = html.Div([

    # Title
    html.H2('Mesh Configuration',
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

    html.Div([
        dcc.Dropdown(id='mesh-dropdown',
                     multi=True),
        dcc.Input(id='mesh-name', placeholder='Enter Mesh Name', type="text"),
        dcc.Slider(id='mesh-energy-slider',
                   min=-5,
                   max=10,
                   step=0.5,
                   value=-3,
                   ),
        html.Br(),
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
        html.Br(),
        html.Button('Submit Mesh', id='submit-mesh-button', n_clicks=0),
        html.P(id='mesh-message'),

        ###############################################################
        # https://openmc.readthedocs.io/en/stable/pythonapi/generated/openmc.Settings.html#openmc.Settings
        html.H2('Run Settings'),

        html.Label('Total Batches'), dcc.Input(id='total-batches', type='number'),
        html.Label('Inactive Batches'), dcc.Input(id='inactive-batches', type='number'),
        html.Label('Particles'), dcc.Input(id='particles', type='number'),
        html.Label('Generations per Batch'), dcc.Input(id='gens-per-batch', type='number'),
        html.Label('Seed'), dcc.Input(id='seed', type='number'),

        html.H4('Run Mode'),
        dcc.Dropdown(id='run-mode', options=[
            {'label': 'Fixed Source', 'value': 'fixed source'},
            {'label': 'Eigenvalue', 'value': 'eigenvalue'},
            {'label': 'Volume', 'value': 'volume'},
            {'label': 'Plot', 'value': 'plot'},
            {'label': 'Particle Restart', 'value': 'particle restart'},
        ]),

        html.H4('Energy Mode'),
        dcc.Dropdown(id='energy-mode', options=[
            {'label': 'Continuous Energy', 'value': 'continuous-energy'},
            {'label': 'Multi-Group', 'value': 'multi-group'},
        ]),
        html.H6('Cutoff'),
        dcc.Dropdown(id='cutoff', options=[
            {'label': 'Weight', 'value': 'weight'},
            {'label': 'Average Weight', 'value': 'weight_avg'},
            {'label': 'Energy', 'value': 'energy'},
        ]),

        # restore_object('model').settings.entropy_mesh = openmc.mesh
        # max_order = None or int
        # multipole_library = 'path'
        # cross_sections = '/cross-sections/cross_sections.xml'
        html.H4('Temperature'),
        dcc.Dropdown(id='temperature', options=[
            {'label': 'Default', 'value': 'default'},
            {'label': 'Method', 'value': 'method'},
            {'label': 'Range', 'value': 'range'},
            {'label': 'Tolerance', 'value': 'tolerance'},
            {'label': 'Multipole', 'value': 'multipole'},
        ]),

        html.H4('Miscellaneous'),
        daq.BooleanSwitch(id='trigger-active', label='Trigger Active', labelPosition='right'),
        # keff_trigger = dict
        # trigger_batch_interval = int
        # trigger_max_batches = int

        daq.BooleanSwitch(id='no-reduce', label='No Reduce', labelPosition='right'),
        daq.BooleanSwitch(id='confidence-intervals', label='Confidence Intervals', labelPosition='right'),
        daq.BooleanSwitch(id='ptables', label='P-Tables', labelPosition='right'),
        daq.BooleanSwitch(id='run-cmfd', label='Run CMFD', labelPosition='right'),
        daq.BooleanSwitch(id='survival-biasing', label='Survival Biasing', labelPosition='right'),
        daq.BooleanSwitch(id='fission-neutrons', label='Create Fission Neutrons', labelPosition='right'),
        # ufs_mesh = openmc.Mesh
        # volume_calculations = iterable of VolumeCalculation
        # resonance_scattering = dict

        html.H4('Outputs'),
        daq.BooleanSwitch(id='output-cross-sections', label='Output Cross-Sections', labelPosition='right', on=True),
        daq.BooleanSwitch(id='output-summary', label='Output Summary', labelPosition='right', on=True),
        daq.BooleanSwitch(id='output-tallies', label='Output Tallies', labelPosition='right', on=True),
        daq.BooleanSwitch(id='cross-sections', label='Output Cross-Sections', labelPosition='right', on=True),
        dcc.Slider(id='verbosity', min=0, max=10, step=1, value=5)

        # restore_object('model').settings.source = Iterable of openmc.Source
        # restore_object('model').settings.state_point = dict
        # restore_object('model').settings.source_point = dict
        # restore_object('model').settings.threads = int
        # restore_object('model').settings.trace = tuple or list
        # restore_object('model').settings.track = tuple or list
    ]),

])

#######################################################################################################################
# Mesh Interface


# TODO: Add multiple mesh filters
# @app.callback(
#     Output('mesh-dropdown', 'options'),
#     [Input('submit-mesh-button', 'n_clicks')],
#     [State('mesh-name', 'value'),
#      # State('mesh-energy-slider', 'value'),
#      State('mesh-x-slider', 'value'),
#      State('mesh-y-slider', 'value'),
#      State('mesh-z-slider', 'value'),
#      State('boundary-range-x', 'value'),
#      State('boundary-range-y', 'value'),
#      State('boundary-range-z', 'value'),
#      State('mesh-dropdown', 'options')])
# def mesh_creation(n_clicks, mesh_name, x_resolution, y_resolution, z_resolution, b_range_x, b_range_y, b_range_z,
#                   mesh_options):
#     if n_clicks > 0:
#         x_width = b_range_x[1] - b_range_x[0]
#         y_width = b_range_y[1] - b_range_y[0]
#         z_height = b_range_z[1] - b_range_z[0]
#
#         if mesh_options is not None:
#             mesh_options.append({'label': mesh_name, 'value': len(mesh_options) + 1})
#         if mesh_options is None:
#             mesh_options = [{'label': mesh_name, 'value': mesh_name}]
#
#         n_clicks = 0
#
#         return mesh_options

#######################################################################################################################
# Settings Interface

# @app.callback(
#     Output('settings-message', 'children'),
#     [State('total-inactive-batches', 'value'),
#      State('generations-per-batch', 'value'),
#      State('particles-input', 'value')]
# )
# def define_settings(total_batches, generations_per_batch, particles):
#     # Make sure this works
#     cross_sections = '/cross-sections/cross_sections.xml'
#
#     return
