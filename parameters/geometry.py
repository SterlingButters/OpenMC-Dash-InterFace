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

    dcc.Store(id='color-stores', storage_type='session'),
    dcc.Store(id='cell-stores', storage_type='session'),
    dcc.Store(id='selected-stores', storage_type='session'),

    html.P("""
        Second, we need to create our geometries. As an overview, since this interface currently
        only supports geometry settings for a standard PWR/BWR i.e. radial planes for fuel 
        rods and rectangular lattice configurations, we will begin by defining pin cells in which our
        fuel & absorbers rods, water holes, etc will reside. Once pin cell regions are defined, you will
        be able to create a rectangular lattice from a selected pin cell and then make individual selections
        to replace those cell regions for which you would prefer a different configuration.  
           """),

    ################################################################################
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
                                  {'label': 'Material3', 'value': 'Material3'}],
                         value=['Material1', 'Material2', 'Material3']),
            dcc.Graph(id='cell-graph'),
            dcc.Input(id='cell-name', placeholder='Enter Cell Name',
                      type='text'),
            html.Button('Commit Configuration to Memory', id='store-cell-button'),
        ],
            style=dict(
                width='70%',
                display='table-cell',
                verticalAlign="top",
            ),
        ),

        html.Div([
            html.H6("List of Colors"),
            dcc.Dropdown(id='colors-dropdown', multi=True,
                         value=['rgb(255, 0, 0)', 'rgb(25, 255, 0)', 'rgb(0, 22, 255)']),
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
    html.Div(style=dict(height=30)),

    ################################################################################
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
              type='number', value=15),
    dcc.Input(id='assembly-y-dimension', placeholder='Enter assembly y-width dimension',
              type='number', value=15),
    dcc.Input(id='assembly-x-number', placeholder='Enter fuel pins in x-dimension',
              type='number', value=15),
    dcc.Input(id='assembly-y-number', placeholder='Enter fuel pins in y-dimension',
              type='number', value=15),
    html.Div(id='assembly-container'),
    html.Div(id='test'),
    html.Div(style=dict(height=30)),

    ################################################################################
    html.H3('Boundaries'),
    html.P("""
        In this section you will define the bounds for the simulation. Your model will 
        usually be contained within this defined volume thus the boundaries defined here 
        will larger than any of those previous.
           """),
    html.P('Pick root geometry from Dropdown'),
    dcc.Dropdown(id='root-cell-option'),

    html.Div([
        html.Div([
            html.H6("X Boundaries"),
            html.Br(),
            dcc.RangeSlider(id='boundary-range-x',
                            min=-1000,
                            max=1000,
                            value=[-100, 100],
                            marks={
                                -1000: {'label': '-1000', 'style': {'color': '#77b0b1'}},
                                0: {'label': '0', 'style': {'color': '#f50'}},
                                1000: {'label': '1000', 'style': {'color': '#f50'}}
                            },
                            allowCross=False,
                            pushable=True),
            html.Br(),
            dcc.RadioItems(id='boundary-type-x',
                           options=[
                               {'label': 'Reflective', 'value': 'reflective'},
                               {'label': 'Vacuum', 'value': 'vacuum'},
                           ],
                           value='vacuum'
                           ),
        ],
            style=dict(
                display='table-cell',
                verticalAlign="top",
                width='25%'
            ),
        ),
        html.Div(style=dict(
            display='table-cell',
            verticalAlign="top",
            width='10%'
        )),
        html.Div([
            html.H6("Y Boundaries"),
            html.Br(),
            dcc.RangeSlider(id='boundary-range-y',
                            min=-1000,
                            max=1000,
                            value=[-100, 100],
                            marks={
                                -1000: {'label': '-1000', 'style': {'color': '#77b0b1'}},
                                0: {'label': '0', 'style': {'color': '#f50'}},
                                1000: {'label': '1000', 'style': {'color': '#f50'}}
                            },
                            allowCross=False,
                            pushable=True,
                            ),
            html.Br(),
            dcc.RadioItems(id='boundary-type-y',
                           options=[
                               {'label': 'Reflective', 'value': 'reflective'},
                               {'label': 'Vacuum', 'value': 'vacuum'},
                           ],
                           value='vacuum'
                           ),
        ],
            style=dict(
                display='table-cell',
                verticalAlign="top",
                width='25%'
            ),
        ),
        html.Div(style=dict(
            display='table-cell',
            verticalAlign="top",
            width='10%'
        )),
        html.Div([
            html.H6("Z Boundaries"),
            html.Br(),
            dcc.RangeSlider(id='boundary-range-z',
                            min=-1000,
                            max=1000,
                            value=[-100, 100],
                            marks={
                                -1000: {'label': '-1000', 'style': {'color': '#77b0b1'}},
                                0: {'label': '0', 'style': {'color': '#f50'}},
                                1000: {'label': '1000', 'style': {'color': '#f50'}}
                            },
                            allowCross=False,
                            pushable=True,
                            ),
            html.Br(),
            dcc.RadioItems(id='boundary-type-z',
                           options=[
                               {'label': 'Reflective', 'value': 'reflective'},
                               {'label': 'Vacuum', 'value': 'vacuum'},
                           ],
                           value='vacuum'
                           ),
        ],
            style=dict(
                display='table-cell',
                verticalAlign="top",
                width='25%'
            ),
        ),

    ], style=dict(
        width='100%',
        display='table',
    ),
    ),

    html.Button('Submit Geometrical Boundaries to Memory', id='submit-boundaries-btn')
])


#######################################################################################################################
# Geometry Interface

###########################################
# Commit colors to memory (options state works but trying to debug other errors and cant find source)
@app.callback(
    Output('color-stores', 'data'),
    [Input('add-color-button', 'n_clicks')],
    [State('color-picker', 'value'),
     State('color-name', 'value'),
     State('color-stores', 'data')]
)
def add_color(click, color, name, data):
    data = data or {'options': [{'label': 'Fuel', 'value': 'rgb(255, 0, 0)'},
                                {'label': 'Clad', 'value': 'rgb(25, 255, 0)'},
                                {'label': 'Water', 'value': 'rgb(0, 22, 255)'}]}

    options = data['options']
    color = 'rgb({}, {}, {})'.format(color['rgb']['r'], color['rgb']['g'], color['rgb']['b'])
    if click > 0 and name is not None:
        options.append({'label': name, 'value': color})

    return data


# Populate from Dropdown
@app.callback(
    Output('colors-dropdown', 'options'),
    [Input('color-stores', 'modified_timestamp')],
    [State('color-stores', 'data')]
)
def add_data(timestamp, data):
    if timestamp is None:
        raise PreventUpdate

    if data:
        return data['options']


###########################################


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

    values = [0]
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
                  height=500,
                  width=500,
                  shapes=shapes)

    figure = dict(data=[heatmap], layout=layout)

    return figure


# Commit Cell to memory
@app.callback(
    Output('cell-stores', 'data'),
    [Input('store-cell-button', 'n_clicks')],
    [State('cell-name', 'value'),
     State('planes-list', 'value'),
     State('material-dropdown', 'value'),
     State('colors-dropdown', 'value'),
     State('cell-stores', 'data')]
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
# @app.callback(
#     Output('store-cell-button', 'disabled'),
#     [Input('cell-name', 'value'),
#      Input('planes-list', 'value'),
#      Input('material-dropdown', 'value')]
# )
# def disable_button(name, planes, materials):
#     if planes is None:
#         print("Must have at least one plane")
#     else:
#         planes = [float(plane) for plane in planes.split(',')]
#         planes.sort()
#
#     if len(planes) > 0 and materials is not None and len(materials) == len(planes) + 1 and name is not None:
#         return False
#     else:
#         return True


#
@app.callback(
    Output('cell-dropdown', 'options'),
    [Input('cell-stores', 'modified_timestamp')],
    [State('cell-stores', 'data')]
)
def store_cell(timestamp, data):
    if timestamp is None:
        raise PreventUpdate

    if data:
        labels = data.keys()
        options = [{'label': label, 'value': label} for label in labels]

        print(data)

        return options


#######################################################################################################################
# Assemblies


@app.callback(
    Output('selected-stores', 'data'),
    [Input('assembly-graph', 'clickData')],
    [State('selected-stores', 'data')]
)
def print_selected_cells(clickData, data):
    data = data or {'selected-cells': []}
    selected_cells = data['selected-cells']

    if clickData:
        x = clickData['points'][0]['x']
        y = clickData['points'][0]['y']
        if [x, y] not in selected_cells:
            selected_cells.append([x, y])
        else:
            selected_cells.remove([x, y])

    return {'selected-cells': selected_cells}


@app.callback(
    Output('test', 'children'),
    [Input('selected-stores', 'modified_timestamp')],
    [State('selected-stores', 'data')]
)
def test(timestamp, data):
    if timestamp is None:
        raise PreventUpdate

    if data:
        print(data)
        return html.P('{}'.format(str(data['selected-cells'])))


@app.callback(
    Output('assembly-container', 'children'),
    [Input('cell-dropdown', 'value'),
     Input('assembly-x-dimension', 'value'),
     Input('assembly-y-dimension', 'value'),
     Input('assembly-x-number', 'value'),
     Input('assembly-y-number', 'value'),
     Input('cell-stores', 'data')]
)
def fill_assembly(selected_cell, assembly_dim_x, assembly_dim_y, assembly_num_x, assembly_num_y, data):
    if data and selected_cell:
        planes = data[selected_cell]['radii']
        planes = planes[::-1]

        pitch_x = assembly_dim_x / assembly_num_x
        pitch_y = assembly_dim_y / assembly_num_y

        # if planes[0] * assembly_num_x > assembly_dim_x or planes[0] * assembly_num_y > assembly_dim_y:
        #     return html.P("Assembly Dimensions and/or Quantities are insensible. You will see this message"
        #                   "if your specifications are causing pins to overlap!")

        # else:
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
                        'line': dict(width=.1),
                        'opacity': .7
                    }

                    shapes.append(shape)

        layout = dict(
            title='Assembly Depiction',
            height=750,
            width=750,

            xaxis=dict(
                range=[-(planes[0] / 2 + (pitch_x - planes[0]) / 2), assembly_num_x],  # pitch_x*assembly_num_x
                showgrid=False,
                zeroline=False,
                fixedrange=True
            ),
            yaxis=dict(
                range=[-(planes[0] / 2 + (pitch_y - planes[0]) / 2), assembly_num_y],
                showgrid=False,
                zeroline=False,
                fixedrange=True
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

        return dcc.Graph(id='assembly-graph', figure=figure)


#######################################################################################################################
# Boundaries

# Store whole-geometry outer boundary and type
# @app.callback(
#     Output('geometry-stores2', 'data'),
#     [Input('submit-boundaries-btn', 'n_clicks')],
#     [State('boundary-range-x', 'value'),
#      State('boundary-range-y', 'value'),
#      State('boundary-range-z', 'value'),
#      State('boundary-type-x', 'value'),
#      State('boundary-type-y', 'value'),
#      State('boundary-type-z', 'value'),
#      State('geometry-stores2', 'data')])
# def set_boundaries(clicks, range_x, range_y, range_z, btype_x, btype_y, btype_z, data):
#     if clicks is None:
#         raise PreventUpdate
#
#     min_x = range_x[0]
#     max_x = range_x[1]
#     min_y = range_y[0]
#     max_y = range_y[1]
#     min_z = range_z[0]
#     max_z = range_z[1]
#
#     return {'X-min': min_x, 'X-max': max_x, 'X-btype': btype_x,
#             'Y-min': min_y, 'Y-max': max_y, 'Y-btype': btype_y,
#             'Z-min': min_z, 'Z-max': max_z, 'Z-btype': btype_y}


if __name__ == '__main__':
    app.run_server(debug=True)
