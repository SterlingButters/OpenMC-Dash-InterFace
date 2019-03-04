import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, State, Input

import openmc
import openmc.model
import openmc.mgxs

import pickle
import redis


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

    ################################################################################
    html.Br(),

    # Periodic Table for Material Selection
    html.Div([
        html.Button('Create Mesh', id='create-mesh-button', n_clicks=0),
        html.Div(id='mesh-config-container'),
        html.A(id='mesh-message'),
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

#######################################################################################################################
# Mesh Interface
mesh_list = []
mesh_filters_list = []


@app.callback(
    Output('mesh-config-container', 'children'),
    [Input('create-mesh-button', 'n_clicks')],)
def invoke_mesh_options(n_clicks):
    if n_clicks == 0:
        return []
    if n_clicks > 0:
        options = html.Div([
                            dcc.Dropdown(id='mesh-dropdown',
                                         multi=True),
                            dcc.Input(id='mesh-name', placeholder='Enter Mesh Name', type="text"),
                            # dcc.Slider(id='mesh-energy-slider',
                            #            min=-5,
                            #            max=10,
                            #            step=0.5,
                            #            value=-3,
                            #            ),
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
                            html.Button('Submit Mesh', id='submit-mesh-button', n_clicks=0)
        ])

        return options


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
def mesh_creation(n_clicks, mesh_name, x_resolution, y_resolution, z_resolution, b_range_x, b_range_y, b_range_z, mesh_options):
    if n_clicks > 0:
        x_width = b_range_x[1] - b_range_x[0]
        y_width = b_range_y[1] - b_range_y[0]
        z_height = b_range_z[1] - b_range_z[0]

        mesh_energy = openmc.Mesh()  # mesh_id=1; Can set mesh id or give name
        mesh_energy.type = 'regular'
        mesh_list.append(mesh_energy)
        mesh_filters_list.append(openmc.MeshFilter(mesh_energy))

        mesh_cartesian = openmc.Mesh(name=mesh_name)
        mesh_cartesian.type = 'regular'
        mesh_cartesian.dimension = [x_resolution, y_resolution, z_resolution]
        mesh_cartesian.lower_left = [b_range_x[0], b_range_y[0], b_range_z[0]]
        mesh_cartesian.width = [x_width/x_resolution, y_width/y_resolution, z_height/z_resolution]
        mesh_list.append(mesh_cartesian)
        mesh_filters_list.append(openmc.MeshFilter(mesh_cartesian))

        if mesh_options is not None:
            mesh_options.append({'label': mesh_name, 'value': len(mesh_options) + 1})
        if mesh_options is None:
            mesh_options = [{'label': mesh_name, 'value': mesh_name}]

        n_clicks = 0

        return mesh_options


if __name__ == '__main__':
    app.run_server(debug=True)
