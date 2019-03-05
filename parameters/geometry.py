import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, State, Input
import dash_daq as daq
import json
from dash.exceptions import PreventUpdate

import plotly.graph_objs as go

import numpy as np
import re

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True

#######################################################################################################################

app.layout = html.Div([
    ################################################################################
    # Title
    html.H2('Geometry Configuration',
            style={
                'position': 'relative',
                'top': '0px',
                'left': '10px',
                'font-family': 'Dosis',
                'display': 'inline',
                'font-size': '4.0rem',
                'color': '#4D637F'
            }),
    html.Div(style=dict(height=20)),
    ################################################################################

    dcc.Store(id='geometry-stores', storage_type='session'),
    html.P("""
        Second, we need to create our geometries. As an overview, since this interface currently
        only supports geometry settings for a standard PWR/BWR i.e. radial planes for fuel 
        rods and rectangular lattice configurations, we will begin by defining pin cells in which our
        fuel & absorbers rods, water holes, etc will reside. Once pin cell regions are defined, you will
        be able to create a rectangular lattice from a selected pin cell and then make individual selections
        to replace those cell regions for which you would prefer a different configuration.  
           """),
    html.H3('Cells'),

    html.Div([
        html.Div([
            html.H6("List of Planes"),
            dcc.Input(id='planes-list', value='.45, .4',
                      placeholder='Enter list of radial planes (comma separated)',
                      type="text", style=dict(height=36)),
        ],
            style=dict(
                display='table-cell',
                verticalAlign="top",
                width='10%'
            ),
        ),

        html.Div([
            html.H6("List of Materials"),
            dcc.Dropdown(id='material-dropdown', multi=True,
                         options=[{'label': 'Material1', 'value': 'Material1'},
                                  {'label': 'Material2', 'value': 'Material2'},
                                  {'label': 'Material3', 'value': 'Material3'}]),
            dcc.Graph(id='cell-graph'),
        ],
            style=dict(
                width='70%',
                display='table-cell',
                verticalAlign="top",
            ),
        ),

        html.Div([
            html.H6("List of Colors"),
            dcc.Dropdown(id='colors-dropdown', multi=True),
            daq.ColorPicker(
                id='color-picker',
                label="Material Color",
                value={'hex': '#ff0000', 'rgb': {'r': 255, 'g': 0, 'b': 0, 'a': 1}}
            ),
            dcc.Input(id='color-name', placeholder='Color Name', type="text", size=26),
            html.Button('Add color to Dropdown', id='add-color-button', n_clicks=0),
        ],
            style=dict(
                width='20%',
                display='table-cell',
                verticalAlign="top",
            ),
        ),
    ], style=dict(
        width='100%',
        display='table',
    ),
    ),

    dcc.Input(id='cell-name', placeholder='Enter Cell Name',
              type='text'),
    html.Button('Commit Configuration to Memory', id='store-cell-button'),
    html.Div(style=dict(height=30)),

    html.H3('Assemblies'),
    html.P("""
        Now that a cell has been successfully created, it is now available for selection in the 
        dropdown below. The selection made from this cell will create an assembly based on the specifications
        of the selected cell. Don't worry, you will be able to pick and choose individual cells to change 
        their specifications if needed e.g. control rods, water holes, etc.
           """),
    html.H6('Cell Selection'),
    dcc.Dropdown(id='cell-dropdown'),
    dcc.Input(id='assembly-x-dimension', placeholder='Enter assembly x-width dimension',
              type='number', value=25),
    dcc.Input(id='assembly-y-dimension', placeholder='Enter assembly y-width dimension',
              type='number', value=25),
    dcc.Input(id='assembly-x-number', placeholder='Enter fuel pins in x-dimension',
              type='number', value=17),
    dcc.Input(id='assembly-y-number', placeholder='Enter fuel pins in y-dimension',
              type='number', value=17),
    dcc.Graph(id='assembly-graph'),
    html.Div(style=dict(height=30)),

    html.H3('Boundaries'),
    html.Button('Set Geometrical Boundaries', id='whole-geometry-button', n_clicks=0),
    html.Div(id='whole-geometry-config-container'),
])


#######################################################################################################################
# Geometry Interface

@app.callback(
    Output('colors-dropdown', 'options'),
    [Input('add-color-button', 'n_clicks')],
    [State('color-picker', 'value'),
     State('color-name', 'value'),
     State('colors-dropdown', 'options')]
)
def add_color(click, color, name, options):
    color = 'rgb({}, {}, {})'.format(color['rgb']['r'], color['rgb']['g'], color['rgb']['b'])
    if click > 0 and name is not None:
        if options is None:
            options = [{'label': name, 'value': color}]
        else:
            options.append({'label': name, 'value': color})

        return options


# Graph Cell from Inputs
@app.callback(
    Output('cell-graph', 'figure'),
    [Input('planes-list', 'value'),
     Input('material-dropdown', 'value'),
     Input('colors-dropdown', 'value')],
)
def create_cell(planes, materials, colors):
    planes = [float(plane) for plane in planes.split(',')]
    planes.sort()

    edge = planes[-1] + 0.25 * planes[-1]
    visible_edge = planes[-1] + 0.1 * planes[-1]
    x = np.linspace(-edge, edge, 250)
    y = np.linspace(-edge, edge, 250)

    colorscale = [[0, 'rgb(255, 255, 255)']]
    if colors is not None and len(colors) >= 1:
        values = np.linspace(0, 1, len(colors) + 1)[1:]
        for value in range(len(colors)):
            colorscale.append([values[value], colors[value]])

    regions = []
    cell_hover = []
    for i in x:
        row = []
        text_row = []
        for j in y:

            if np.sqrt(i ** 2 + j ** 2) < planes[0]:
                # For HoverText
                if materials is None:
                    text_row.append('Region 1')
                else:
                    text_row.append(materials[0])

                # For Color
                if colors is not None:
                    row.append(values[0])
                else:
                    row.append(0)

            if np.sqrt(i ** 2 + j ** 2) > planes[-1]:
                # For HoverText
                if materials is not None and len(materials) > len(planes):
                    text_row.append(materials[-1])
                else:
                    text_row.append('Region {}'.format(len(planes) + 1))

                # For Colors
                if -visible_edge < i < visible_edge and -visible_edge < j < visible_edge:
                    if colors is not None and len(colors) > len(planes):
                        row.append(values[-1])
                    else:
                        row.append(0)
                else:
                    row.append(0)

            for k in range(len(planes) - 1):
                # For HoverText
                if planes[k] < np.sqrt(i ** 2 + j ** 2) < planes[k + 1]:
                    if materials is not None and len(materials) > 1:
                        text_row.append(materials[k + 1])
                    else:
                        text_row.append('Region {}'.format(k + 2))

                # For Colors
                if planes[k] < np.sqrt(i ** 2 + j ** 2) < planes[k + 1]:
                    if colors is not None and len(colors) > 1:
                        row.append(values[k + 1])
                    else:
                        row.append(0)

        regions.append(row)
        cell_hover.append(text_row)

    heatmap = go.Heatmap(z=regions,
                         x=x,
                         y=y,
                         hoverinfo='x+y+text',
                         text=cell_hover,
                         colorscale=colorscale,
                         opacity=0.5,
                         showscale=False)

    shapes = []
    for plane in planes:
        shape = {
            'type': 'circle',
            'x0': -plane,
            'y0': -plane,
            'x1': plane,
            'y1': plane,
            'line': {
                'width': 4,
            },
            'opacity': 1
        }

        shapes.append(shape)

    layout = dict(title='Cell Region Depiction',
                  xaxis=dict(fixedrange=True,
                             range=[-visible_edge, visible_edge]),
                  yaxis=dict(fixedrange=True,
                             range=[-visible_edge, visible_edge]),
                  height=750,
                  width=750,
                  shapes=shapes)

    figure = dict(data=[heatmap], layout=layout)

    return figure


# Commit Cell to memory
@app.callback(
    Output('geometry-stores', 'data'),
    [Input('store-cell-button', 'n_clicks')],
    [State('cell-name', 'value'),
     State('planes-list', 'value'),
     State('material-dropdown', 'value'),
     State('colors-dropdown', 'value'),
     State('geometry-stores', 'data')]
)
def store_cell(clicks, name, planes, materials, colors, data):
    if clicks is None:
        raise PreventUpdate

    planes = [float(plane) for plane in planes.split(',')]
    planes.sort()

    data = data or {}

    data.update({'{}'.format(name): {'radii': planes,
                                     'materials': materials,
                                     'colors': colors}})

    return data


# Disable Button to commit cell to memory if missing Information
@app.callback(
    Output('store-cell-button', 'disabled'),
    [Input('cell-name', 'value'),
     Input('planes-list', 'value'),
     Input('material-dropdown', 'value')]
)
def disable_button(name, planes, materials):
    if planes is None:
        print("Must have at least one plane")
    else:
        planes = [float(plane) for plane in planes.split(',')]
        planes.sort()

    if len(planes) > 0 and materials is not None and len(materials) == len(planes) + 1 and name is not None:
        return False
    else:
        return True


#
@app.callback(
    Output('cell-dropdown', 'options'),
    [Input('geometry-stores', 'modified_timestamp')],
    [State('geometry-stores', 'data')]
)
def store_cell(timestamp, data):
    if timestamp is None:
        raise PreventUpdate

    if data:
        labels = data.keys()
        print(labels)

        options = [{'label': label, 'value': label} for label in labels]

        print(data)

        return options


#######################################################################################################################


# Fill Assembly
@app.callback(
    Output('assembly-graph', 'figure'),
    [Input('cell-dropdown', 'value'),
     Input('assembly-x-dimension', 'value'),
     Input('assembly-y-dimension', 'value'),
     Input('assembly-x-number', 'value'),
     Input('assembly-y-number', 'value'),
     Input('geometry-stores', 'data')]
)
def fill_assembly(selected_cell, assembly_dim_x, assembly_dim_y, assembly_num_x, assembly_num_y, data):
    planes = data[selected_cell]['radii']
    planes = planes[::-1]

    pitch_x = assembly_dim_x / assembly_num_x
    pitch_y = assembly_dim_y / assembly_num_y

    # TODO, if dimensions and quanitities are insensible, limit and explain to user
    # if planes[0]*assembly_num_x > assembly_dim_x \
    #     or planes[0]*assembly_num_y > assembly_dim_y:
    #         assembly_dim_x = planes[0]*assembly_num_x
    #         assembly_dim_y = planes[0]*assembly_num_y

    colors = data[selected_cell]['colors']
    assembly_region = np.ones((assembly_num_y, assembly_num_x))
    colorscale = [[0, 'rgb(255, 255, 255)'], [1, colors[-1]]]
    colors = colors[::-1][1:]

    # Display universe name and location
    assembly_hover = []
    for a in range(assembly_dim_y):
        row = []
        for b in range(assembly_dim_x):
            row.append('Universe')
        assembly_hover.append(row)

    # Invert Matrices
    assembly_hover = assembly_hover[::-1]

    shapes = []
    print(colors)
    for p in range(len(planes)):
        color = colors[p]
        for a in range(assembly_num_y):
            for b in range(assembly_num_x):
                shape = {
                    'type': 'circle',
                    'x0': b - planes[p] / pitch_x / 2,
                    'y0': a - planes[p] / pitch_y / 2,
                    'x1': b - planes[p] / pitch_x / 2 + planes[p] / pitch_x,
                    'y1': a - planes[p] / pitch_y / 2 + planes[p] / pitch_y,
                    'fillcolor': color,
                    'opacity': .7
                }

                shapes.append(shape)

    layout = dict(
        title='Assembly Depiction',
        height=1000,
        width=1000,

        xaxis=dict(
            range=[-(planes[0] / 2 + (pitch_x - planes[0]) / 2), assembly_num_x],  # pitch_x*assembly_num_x
            showgrid=False,
            zeroline=False,
            # fixedrange=True
        ),
        yaxis=dict(
            range=[-(planes[0] / 2 + (pitch_y - planes[0]) / 2), assembly_num_y],
            showgrid=False,
            zeroline=False,
            # fixedrange=True
        ),
        shapes=shapes,
    )

    heatmap = go.Heatmap(z=assembly_region,
                         hoverinfo='x+y+text',
                         text=assembly_hover,
                         colorscale=colorscale,
                         showscale=False,
                         opacity=0.5)
    data = [heatmap]

    figure = dict(data=data, layout=layout)

    return figure


# ###################################
#
#
# # Invoke Geometrical Boundary Options
# @app.callback(
#     Output('whole-geometry-config-container', 'children'),
#     [Input('whole-geometry-button', 'n_clicks')],)
# def invoke_whole_geometry_options(n_clicks):
#     if n_clicks > 0:
#         options = html.Div([html.A('Pick root geometry from Dropdown'),
#                             dcc.Dropdown(id='root-cell-option'),
#                             html.Br(),
#                             dcc.RangeSlider(id='boundary-range-x',
#                                             min=-1000,
#                                             max=1000,
#                                             value=[-20, 20],
#                                             marks={
#                                                 -1000: {'label': '-1000', 'style': {'color': '#77b0b1'}},
#                                                 0: {'label': '0', 'style': {'color': '#f50'}},
#                                                 1000: {'label': '1000', 'style': {'color': '#f50'}}
#                                             },
#                                             allowCross=False),
#                             html.Br(),
#                             dcc.RadioItems(id='boundary-type-x',
#                                            options=[
#                                                 {'label': 'Reflective', 'value': 'reflective'},
#                                                 {'label': 'Vacuum', 'value': 'vacuum'},
#                                             ],
#                                            value='vacuum'
#                                            ),
#                             html.Br(),
#                             dcc.RangeSlider(id='boundary-range-y',
#                                             min=-1000,
#                                             max=1000,
#                                             value=[-20, 20],
#                                             marks={
#                                                 -1000: {'label': '-1000', 'style': {'color': '#77b0b1'}},
#                                                 0: {'label': '0', 'style': {'color': '#f50'}},
#                                                 1000: {'label': '1000', 'style': {'color': '#f50'}}
#                                             },
#                                             allowCross=False),
#                             html.Br(),
#                             dcc.RadioItems(id='boundary-type-y',
#                                            options=[
#                                                {'label': 'Reflective', 'value': 'reflective'},
#                                                {'label': 'Vacuum', 'value': 'vacuum'},
#                                            ],
#                                            value='vacuum'
#                                            ),
#                             html.Br(),
#                             dcc.RangeSlider(id='boundary-range-z',
#                                             min=-1000,
#                                             max=1000,
#                                             value=[-100, 100],
#                                             marks={
#                                                 -1000: {'label': '-1000', 'style': {'color': '#77b0b1'}},
#                                                 0: {'label': '0', 'style': {'color': '#f50'}},
#                                                 1000: {'label': '1000', 'style': {'color': '#f50'}}
#                                             },
#                                             allowCross=False),
#                             html.Br(),
#                             dcc.RadioItems(id='boundary-type-z',
#                                            options=[
#                                                {'label': 'Reflective', 'value': 'reflective'},
#                                                {'label': 'Vacuum', 'value': 'vacuum'},
#                                            ],
#                                            value='vacuum'
#                                            ),
#                             html.Br()])
#
#         return options


# @app.callback(
#     Output('root-cell-option', 'options'),
# )
# def root_cell_fill():   # Goes through cells first, then assemblies
#     options = []
#     for universe in range(len(all_universes)):
#         options.append(
#             {'label': all_universes[universe].name, 'value': universe}
#         )
#     return options
#
# @app.callback(
#     Output('root-cell-placeholder', 'children'),
#     [Input('root-option', 'value')]
# )
# def root_cell_fill(root_selection):
#     root_cell.fill = root_selection
#     return
#
#
# TODO: Change range slider values to dimensions of the chosen root cell
# TODO: Change range slider max/min values based on ^^
# TODO: Change range slider marks based on ^^
# @app.callback(
#     Output('boundary-range-x', 'value'),
#     [Input('root-cell-option', 'value')]
# )
# def change_x_slider_value(selected_root):
#     # TODO: so far, this only accounts for cells, not assemblies
#     dimension = cell_bounds[selected_root]
#     values = [-(dimension + .2*dimension), (dimension + .2*dimension)]
#     return values
#
#
# # Set whole-geometry outer boundary and type
# @app.callback(
#     Output('geometry-boundary-placeholder', 'value'),                       # TODO: Offer 2 different planes: cylindrical and box
#     [Input('boundary-range-x', 'value'),
#      Input('boundary-range-y', 'value'),
#      Input('boundary-range-z', 'value'),
#      Input('boundary-type-x', 'value'),
#      Input('boundary-type-y', 'value'),
#      Input('boundary-type-z', 'value')])
# def set_boundaries(range_x, range_y, range_z, btype_x, btype_y, btype_z):   # TODO: Allow different boundary types for any surface
#     min_x = openmc.XPlane(x0=range_x[0], boundary_type=btype_x)
#     max_x = openmc.XPlane(x0=range_x[1], boundary_type=btype_x)
#     min_y = openmc.YPlane(y0=range_y[0], boundary_type=btype_y)
#     max_y = openmc.YPlane(y0=range_y[1], boundary_type=btype_y)
#     min_z = openmc.ZPlane(z0=range_z[0], boundary_type=btype_z)
#     max_z = openmc.ZPlane(z0=range_z[1], boundary_type=btype_z)
#     root_cell.region = +min_x & -max_x & \
#                        +min_y & -max_y & \
#                        +min_z & -max_z
#     return


if __name__ == '__main__':
    app.run_server(debug=True)
