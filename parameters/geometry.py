import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, State, Input

import plotly.graph_objs as go

import numpy as np
import re


app = dash.Dash()
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

    ################################################################################
    html.Br(),

    # Periodic Table for Material Selection
    html.Div([

        html.A(id='chosen-element'),
        html.Div(id='composition-option-container'),
        html.A(id='isotope-message-update'),

        html.Button('Create Cell', id='cell-geometry-button', n_clicks=0),
        html.Div(id='cell-geometry-config-container'),

        html.Div(id='assembly-geometry-config-container'),

        html.Button('Set Geometrical Boundaries', id='whole-geometry-button', n_clicks=0),
        html.Div(id='whole-geometry-config-container'),
    ]),

])

#######################################################################################################################
# Geometry Interface


# Initiate cell geometry config with button
@app.callback(
    Output('cell-geometry-config-container', 'children'),
    [Input('cell-geometry-button', 'n_clicks')],)
def invoke_cell_geometry_options(n_clicks):
    # TODO: Below works but must find way to implement fill_region function on arbitrary number of graphs
    geometry_ui_list = []
    if n_clicks < 5:
        for i in range(n_clicks):
            geometry_ui_list.extend([dcc.Graph(id='cell-graph-{}'.format(i+1)),
                                    dcc.Input(id='planes-list-{}'.format(i+1), value='.45, .4', placeholder='Enter list of radial planes (comma separated)',
                                              type="text"),
                                    html.Button('Fill Region', id='fill-region-button-{}'.format(i+1), n_clicks=0),
                                    html.A(id='click-register-{}'.format(i+1)),
                                    html.Br(),
                                    ])

    if n_clicks == 5:
        n_clicks = 4

    if n_clicks > 0:
        geometry_ui_list.extend([html.Button('Create Assembly', id='assembly-geometry-button')])

    options = html.Div(geometry_ui_list)
    return options


# #######################################################################################################################
# @app.callback(
#     Output('click-register-1', 'children'),
#     [Input('cell-graph-1', 'clickData')])
# def click_register_function_1(clickData):
#     region = 0
#     click_x = 0
#     click_y = 0
#     if clickData is not None:
#         if 'points' in clickData:
#             point = clickData['points'][0]
#             if 'text' in point:
#                 region = int(re.search(r'\d+', point['text']).group())
#             if 'x' in point:
#                 click_x = point['x']
#             if 'y' in point:
#                 click_y = point['y']
#         return [region, click_x, click_y]
#
#
# # Fill Region
# @app.callback(
#     Output('cell-graph-1', 'figure'),
#     [Input('planes-list-1', 'value'),
#      Input('fill-region-button-1', 'n_clicks')],
#     [State('material-dropdown', 'value'),
#      State('cell-graph-1', 'clickData')]
# )
# def fill_region_1(planes, n_clicks, selected_material, clickData):
#
#     if selected_material == None:
#         print("Please select material from dropdown")
#
#     planes = [float(plane) for plane in planes.split(',')]
#     planes.sort()
#
#     edge = planes[-1]
#     x = np.linspace(-edge, edge, 250)
#     y = np.linspace(-edge, edge, 250)
#
#     regions = []
#     cell_hover = []
#     # Normal Display
#     for i in x:
#         row = []
#         text_row = []
#         for j in y:
#
#             if np.sqrt(i ** 2 + j ** 2) < planes[0]:
#                 row.append(100)      # <- Arbitrary number to adjust color
#                 text_row.append('Region 1')
#
#             if np.sqrt(i ** 2 + j ** 2) > planes[-1]:
#                 row.append(75)      # <- Arbitrary number to adjust color
#                 text_row.append('Region {}'.format(len(planes) + 1))
#
#             for k in range(len(planes) - 1):
#                 if planes[k] < np.sqrt(i ** 2 + j ** 2) < planes[k + 1]:
#                     row.append(k*3)  # <- Arbitrary number to adjust color
#                     text_row.append('Region {}'.format(k + 2))
#         regions.append(row)
#         cell_hover.append(text_row)
#
#     ######################################################
#     # Fill region in OpenMC
#     outer_radii = []
#     for plane in planes:
#         outer_radii.append(openmc.ZCylinder(x0=0, y0=0, R=plane, name='{} Outer Radius'))
#
#     print(outer_radii)
#
#     # Initialize region
#     click_x = 0
#     click_y = 0
#     if clickData is not None:
#         if 'points' in clickData:
#             point = clickData['points'][0]
#             if 'x' in point:
#                 click_x = point['x']
#             if 'y' in point:
#                 click_y = point['y']
#
#         new_hover = []
#
#         if n_clicks > 0:
#
#             # Change graph on Click # TODO: Figure out why new text wont show up
#             if 0 < np.sqrt(click_x ** 2 + click_y ** 2) < planes[0]:
#                 cell_filling = openmc.Cell(name='{}'.format(MATERIALS[selected_material]),
#                                            fill=MODEL.materials[selected_material],
#                                            region=-outer_radii[0])
#                 CELL_FILLINGS.append(cell_filling)
#                 store_object('cell-fillings', CELL_FILLINGS)
#
#                 for row_ in cell_hover:
#                     for text in row_:
#                         new_hover.append(text.replace('Region 1', '{} Region'.format(MATERIALS[selected_material])))
#
#             if np.sqrt(click_x ** 2 + click_y ** 2) > planes[-1]:
#                 cell_filling = openmc.Cell(name='{}'.format(MATERIALS[selected_material]),
#                                            fill=MODEL.materials[selected_material],
#                                            region=+outer_radii[-1])
#                 CELL_FILLINGS.append(cell_filling)
#                 store_object('cell-fillings', CELL_FILLINGS)
#
#                 for row_ in cell_hover:
#                     for text in row_:
#                         new_hover.append(text.replace('Region {}'.format(len(planes) + 1),
#                                                       '{} Region'.format(MATERIALS[selected_material])))
#
#             for k in range(len(planes) - 1):
#                 if planes[k] < np.sqrt(click_x ** 2 + click_y ** 2) < planes[k + 1]:
#                     cell_filling = openmc.Cell(name='{}'.format(MATERIALS[selected_material]),
#                                                fill=MODEL.materials[selected_material],
#                                                region=+outer_radii[k] & -outer_radii[k + 1])
#                     CELL_FILLINGS.append(cell_filling)
#                     store_object('cell-fillings', CELL_FILLINGS)
#
#                     for row_ in cell_hover:
#                         for text in row_:
#                             new_hover.append(text.replace('Region {}'.format(k + 2),
#                                                           '{} Region'.format(MATERIALS[selected_material])))
#
#             n_clicks = 0
#
#         cell_hover = new_hover
#
#     CELL_FILLINGS = restore_object('cell-fillings')
#     print(CELL_FILLINGS)
#
#     cell_universe = openmc.Universe(name='{} Cell'.format(MATERIALS[selected_material]))
#     cell_universe.add_cells(CELL_FILLINGS)
#     print(cell_universe)
#
#     # # Add completely filled cell universe to list of universes
#     if len(CELL_FILLINGS) == len(planes)+1:
#         CELL_UNIVERSES = restore_object('cell-universes')
#         CELL_UNIVERSES.append(cell_universe)
#         store_object('cell-universes', CELL_UNIVERSES)
#
#     ######################################################
#
#     heatmap = go.Heatmap(z=regions,
#                          x=x,
#                          y=y,
#                          hoverinfo='x+y+text',
#                          text=cell_hover,
#                          opacity=0.5,
#                          showscale=False)
#
#     data = [heatmap]
#     shapes = []
#
#     for plane in planes:
#         shape = {
#             'type': 'circle',
#             'x0': -plane,
#             'y0': -plane,
#             'x1': plane,
#             'y1': plane,
#             'line': {
#                 'width': 4,
#             },
#             'opacity': 1
#         }
#
#         shapes.append(shape)
#
#     layout = dict(title='Cell Region Depiction',
#                   height=1000,
#                   width=1000,
#                   shapes=shapes)
#
#     figure = dict(data=data, layout=layout)
#
#     return figure
#
#
# #######################################################################################################################
#
# # Invoke assembly geometry options
# @app.callback(
#     Output('assembly-geometry-config-container', 'children'),
#     [Input('assembly-geometry-button', 'n_clicks')],)
# def invoke_assembly_geometry_options(n_clicks):
#     if n_clicks > 0:
#         options = html.Div([
#             html.Br(),
#             dcc.Graph(id='assembly-graph'),
#             dcc.Dropdown(id='full-assembly-dropdown',),
#             dcc.Input(id='assembly-x-dimension', placeholder='Enter assembly x-width dimension',
#                       type='number', value=25),
#             dcc.Input(id='assembly-y-dimension', placeholder='Enter assembly y-width dimension',
#                       type='number', value=25),
#             dcc.Input(id='assembly-x-number', placeholder='Enter fuel pins in x-dimension',
#                       type='number', value=17),
#             dcc.Input(id='assembly-y-number', placeholder='Enter fuel pins in y-dimension',
#                       type='number', value=17),
#             html.Br(),
#           ])
#         return options
#
#
# # Fill Assembly
# @app.callback(
#     Output('assembly-graph', 'figure'),
#     [Input('assembly-x-dimension', 'value'),
#      Input('assembly-y-dimension', 'value'),
#      Input('assembly-x-number', 'value'),
#      Input('assembly-y-number', 'value'),
#      Input('planes-list-1', 'value'),
#      Input('assembly-graph', 'clickData')
#      # Input('full-assembly-dropdown', 'value'),
#      ]
# )
# def fill_assembly(assembly_dim_x, assembly_dim_y, assembly_num_x, assembly_num_y, planes, clickData):
#
#     planes = [float(plane) for plane in planes.split(',')]
#     planes.sort()
#     planes = planes[::-1]
#
#     pitch_x = assembly_dim_x/assembly_num_x
#     pitch_y = assembly_dim_y/assembly_num_y
#
#     # TODO, if dimensions and quanitities are insensible, limit and explain to user
#     # if planes[0]*assembly_num_x > assembly_dim_x \
#     #     or planes[0]*assembly_num_y > assembly_dim_y:
#     #         assembly_dim_x = planes[0]*assembly_num_x
#     #         assembly_dim_y = planes[0]*assembly_num_y
#
#     assembly_region = np.ones((assembly_num_y, assembly_num_x))
#
#     # Display universe name and location
#     assembly_hover = []
#     for a in range(assembly_dim_y):
#         row = []
#         for b in range(assembly_dim_x):
#             row.append('Universe')
#         assembly_hover.append(row)
#
#     # Invert Matrices
#     assembly_hover = assembly_hover[::-1]
#
#     shapes = []
#     SHAPES = restore_object('all-shapes')
#     for outer in planes:
#         # TODO: Use Markers instead of shapes
#         color = 'rgb({}, {}, {}'.format(outer*255, outer*255, outer*255)
#         for a in range(assembly_num_y):
#             for b in range(assembly_num_x):
#                 shape = {
#                     'type': 'circle',
#                     'x0': b - outer/pitch_x / 2,
#                     'y0': a - outer/pitch_y / 2,
#                     'x1': b - outer/pitch_x / 2 + outer/pitch_x,
#                     'y1': a - outer/pitch_y / 2 + outer/pitch_y,
#                     'fillcolor': color,
#                     'opacity': .5
#                 }
#
#                 SHAPES.append(shape)
#                 shapes.append(shape)
#
#     click_x = click_y = None
#     if clickData is not None:
#         if 'points' in clickData:
#             point = clickData['points'][0]
#
#             if 'x' in point:
#                 click_x = point['x']
#             if 'y' in point:
#                 click_y = point['y']
#
#         if (click_x, click_y) not in SELECTED_CELLS:
#
#
#         else:
#
#     print(SELECTED_CELLS)
#
#     layout = dict(
#         title='Assembly Depiction',
#         height=1000,
#         width=1000,
#
#         xaxis=dict(
#             range=[-(planes[0]/2 + (pitch_x-planes[0])/2), assembly_num_x],  # pitch_x*assembly_num_x
#             showgrid=False,
#             zeroline=False
#         ),
#         yaxis=dict(
#             range=[-(planes[0] / 2 + (pitch_y - planes[0]) / 2), assembly_num_y],
#             showgrid=False,
#             zeroline=False
#         ),
#         shapes=shapes,
#     )
#
#     heatmap = go.Heatmap(z=assembly_region,
#                          hoverinfo='x+y+text',
#                          text=assembly_hover,
#                          opacity=0.5)
#     data = [heatmap]
#
#     figure = dict(data=data, layout=layout)
#
#     return figure
#
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
