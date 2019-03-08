# TODO: Mesh/Scoring/Settings in one

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, State, Input

app = dash.Dash()
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([
    ################################################################################
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

    # Periodic Table for Material Selection
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
        html.A('Enter mesh x-resolution'),
        dcc.Slider(id='mesh-x-slider',
                   min=1,
                   max=1000,
                   step=1,
                   value=100,
                   marks={i: i for i in range(0, 1000, 100)},
                   ),
        html.Br(),
        html.A('Enter mesh y-resolution'),
        dcc.Slider(id='mesh-y-slider',
                   min=1,
                   max=1000,
                   step=1,
                   value=100,
                   marks={i: i for i in range(0, 1000, 100)},
                   ),
        html.Br(),
        html.A('Enter mesh z-resolution'),
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
    ]),

])

#######################################################################################################################
# Mesh Interface


# TODO: Add multiple mesh filters
@app.callback(
    Output('mesh-dropdown', 'options'),
    [Input('submit-mesh-button', 'n_clicks')],
    [State('mesh-name', 'value'),
     # State('mesh-energy-slider', 'value'),
     State('mesh-x-slider', 'value'),
     State('mesh-y-slider', 'value'),
     State('mesh-z-slider', 'value'),
     State('boundary-range-x', 'value'),
     State('boundary-range-y', 'value'),
     State('boundary-range-z', 'value'),
     State('mesh-dropdown', 'options')])
def mesh_creation(n_clicks, mesh_name, x_resolution, y_resolution, z_resolution, b_range_x, b_range_y, b_range_z,
                  mesh_options):
    if n_clicks > 0:
        x_width = b_range_x[1] - b_range_x[0]
        y_width = b_range_y[1] - b_range_y[0]
        z_height = b_range_z[1] - b_range_z[0]

        if mesh_options is not None:
            mesh_options.append({'label': mesh_name, 'value': len(mesh_options) + 1})
        if mesh_options is None:
            mesh_options = [{'label': mesh_name, 'value': mesh_name}]

        n_clicks = 0

        return mesh_options

#######################################################################################################################
# Settings Interface

# https://openmc.readthedocs.io/en/stable/pythonapi/generated/openmc.Settings.html#openmc.Settings
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
# settings.run_mode = 'fixed source', ‘eigenvalue’, ‘volume’, ‘plot’, ‘particle restart’
# Resonance Scattering


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

if __name__ == '__main__':
    app.run_server(debug=True)
