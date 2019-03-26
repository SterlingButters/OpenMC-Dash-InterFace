import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import numpy as np
import plotly.graph_objs as go
from dash.dependencies import Output, State, Input
from dash.exceptions import PreventUpdate

from app import app

layout = html.Div([
    html.H2('Geometry Configuration',
            style={
                'position': 'relative',
                'top': '0px',
                'left': '10px',
                'font-family': 'Dosis',
                'display': 'inline',
                'font-size': '4.0rem',
                'color': 'rgb(76, 1, 3)'
            }),
    html.Div(style=dict(height=20)),

    html.P("""
        Second, we need to create our geometries. As an overview, since this interface currently
        only supports geometry settings for a standard PWR/BWR i.e. radial planes for fuel 
        rods and rectangular lattice configurations, we will begin by defining pin cells in which our
        fuel & absorbers rods, water holes, etc will reside. Once pin cell regions are defined, you will
        be able to create a rectangular lattice from a selected pin cell and then make individual selections
        to replace those cell regions for which you would prefer a different configuration. When making selections,
        use the selection tool as opposed to merely clicking. While clicking will work, the selection tool will 
        work better aesthetically.
           """),

    ################################################################################
    html.H3('Cells'),

    html.Div([
        html.Div([
            html.H6("List of Planes"),
            dcc.Input(id='planes-list', value='.45, .4',
                      placeholder='Enter list of radial planes (comma separated)',
                      type="text", style=dict(height=36)), html.Br(),
            daq.NumericInput(id='cell-pitch-x',
                             min=0,
                             max=5,
                             value=1.26,
                             label='Pin Cell Pitch X',
                             labelPosition='top',
                             size=200,
                             style=dict(float='left'),
                             ),
            daq.NumericInput(id='cell-pitch-y',
                             min=0,
                             max=5,
                             value=1.26,
                             label='Pin Cell Pitch Y',
                             labelPosition='top',
                             size=200,
                             style=dict(float='left'),
                             ),
            daq.NumericInput(id='cell-height',
                             min=0,
                             value=200,
                             label='Pin Cell Height',
                             labelPosition='top',
                             size=200,
                             style=dict(float='left'),
                             )
        ],
            style=dict(
                display='table-cell',
                verticalAlign="top",
                width='10%'
            ),
        ),

        html.Div([
            html.H6("List of Materials"),
            # TODO: Remove these options once app is complete
            dcc.Dropdown(id='material-dropdown', multi=True,
                         options=[{'label': 'Fuel', 'value': 'Fuel'},
                                  {'label': 'Clad', 'value': 'Clad'},
                                  {'label': 'Water', 'value': 'Water'}],
                         value=['Fuel', 'Clad', 'Water']),
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
        their specifications if needed e.g. control rods, water holes, etc. A little description on how to do this:
        Locations of selected cells will be displayed someplace below - this is your main guide when inserting 
        cell universes into the assembly. Keeping track of this information is important because it does not reset once
        an injection is made and this may initially seem a bit unintuitive. Your first step is to make a selection. 
        By clicking on a cell universe multiple times, you may select and deselect the universe from your list of 
        indices. Once you are content with the selection you have made, you may choose what type of cell universe you 
        would like to inject into the chosen indices. You may also "overwrite" other cell universes, i.e. priority is 
        given to your most recent injection. So, if there are indices for cell universes of a type other than your 
        current selection that match your currently selected indices, those indices will be removed from the other cell indices 
        (ones not selected).
           """),
    html.H6('Cell Selection'),
    html.Div([
        html.Div([
            html.Div(style=dict(height=40)),
            html.P("""
                The dropdown below will fill the entire assembly with cells of that type.
                   """),
            dcc.Dropdown(id='cell-dropdown'),
            html.P("X-pins [#]"),
            dcc.Input(id='assembly-x-number', placeholder='Enter fuel pins in x-dimension',
                      type='number', value=15),
            html.P("Y-pins [#]"),
            dcc.Input(id='assembly-y-number', placeholder='Enter fuel pins in y-dimension',
                      type='number', value=15),
            html.P("""
                The dropdown below is used to specify the cell type that is to be used to replace
                only the selected cells.
            """),
            dcc.Dropdown(id='injection-cell'),
            html.P("Selected Cells: "), html.Div(id='display-selected'),
            html.Button('Submit cell into selection(s)', id='submit-selected-btn'),

            # TODO: Link to Callback
            html.Div(id='cell-preview'),
        ],
            style=dict(
                width='35%',
                display='table-cell',
                verticalAlign="top",
            ),
        ),
        html.Div(style=dict(
            width='10%',
            display='table-cell',
            verticalAlign="top",
        ),
        ),
        html.Div([
            dcc.Graph(id='assembly-graph')
        ],
            style=dict(
                width='55%',
                display='table-cell',
                verticalAlign="top",
            ),
        )
    ], style=dict(
        width='100%',
        display='table',
    ),
    ),
    html.Br(),
    dcc.Input(id='assembly-name', placeholder='Enter Assembly Name', size=70, type='text'),
    html.Button('Store Assembly', id='store-assembly-btn', n_clicks=0),
    html.Div(style=dict(height=30)),

    ################################################################################
    html.H3('Core (non-functional - in progress)'),
    html.P("""
        Now that you have created several assemblies, it is time to insert those into our core. 
        Below, there is a blank map of a core to fill with assemblies. The map corresponds to your 
        specified number of assemblies in each dimension. Simply
           """),
    html.P("Number of assemblies in x dimension"),
    dcc.Input(id='core-x-dim', placeholder='Enter Assemblies in x-dimension',
              type='number', value=20),
    html.P("Number of assemblies in y dimension"),
    dcc.Input(id='core-y-dim', placeholder='Enter Assemblies in y-dimension',
              type='number', value=20),
    html.Br(),
    dcc.Dropdown('assembly-dropdown'),
    html.Br(),
    html.Button('Inject Assembly into Core', id='inject-assembly-btn'),
    html.Div(id='display-assembly-indices'),
    dcc.Graph(id='core-graph'),
    html.Div(id='debug'),

    ################################################################################
    html.H3('Root Geometry'),
    html.P('This is the geometry that will be modelled in the simulation. You are able to choose from'
           'any of the past geometries that you created to include cells, assemblies, and full-core.'),
    html.P('Pick root geometry from Dropdown'),
    dcc.Dropdown(id='root-dropdown'),

    ################################################################################

    html.H3('Boundaries'),
    html.P("""
        In this section you will define the bounds for the simulation. Your model will 
        usually be contained within this defined volume thus the boundaries defined here 
        will larger than any of those previous.
           """),
    html.Div([
        html.Div([
            html.H6("X Boundaries"),
            html.Br(),
            dcc.RangeSlider(id='boundary-range-x',
                            min=-100,
                            max=100,
                            value=[-10, 10],
                            marks={
                                -100: {'label': '-100', 'style': {'color': '#77b0b1'}},
                                -50: {'label': '-50', 'style': {'color': '#77b0b1'}},
                                -10: {'label': '-10', 'style': {'color': '#77b0b1'}},
                                0: {'label': '0', 'style': {'color': '#f50'}},
                                10: {'label': '10', 'style': {'color': '#77b0b1'}},
                                50: {'label': '50', 'style': {'color': '#77b0b1'}},
                                100: {'label': '100', 'style': {'color': '#77b0b1'}}
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
                            min=-100,
                            max=100,
                            value=[-10, 10],
                            marks={
                                -100: {'label': '-100', 'style': {'color': '#77b0b1'}},
                                -50: {'label': '-50', 'style': {'color': '#77b0b1'}},
                                -10: {'label': '-10', 'style': {'color': '#77b0b1'}},
                                0: {'label': '0', 'style': {'color': '#f50'}},
                                10: {'label': '10', 'style': {'color': '#77b0b1'}},
                                50: {'label': '50', 'style': {'color': '#77b0b1'}},
                                100: {'label': '100', 'style': {'color': '#77b0b1'}}
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
                            min=-100,
                            max=100,
                            value=[-10, 10],
                            marks={
                                -100: {'label': '-100', 'style': {'color': '#77b0b1'}},
                                -50: {'label': '-50', 'style': {'color': '#77b0b1'}},
                                -10: {'label': '-10', 'style': {'color': '#77b0b1'}},
                                0: {'label': '0', 'style': {'color': '#f50'}},
                                10: {'label': '10', 'style': {'color': '#77b0b1'}},
                                50: {'label': '50', 'style': {'color': '#77b0b1'}},
                                100: {'label': '100', 'style': {'color': '#77b0b1'}}
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
    html.Button('Submit Geometrical Boundaries to Memory', id='submit-geometry-btn')
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
    data = data or {'options': [{'label': 'Red', 'value': 'rgb(255, 0, 0)'},  # TODO: Get rid of this eventually
                                {'label': 'Green', 'value': 'rgb(25, 255, 0)'},
                                {'label': 'Blue', 'value': 'rgb(0, 22, 255)'},
                                ]}

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
    [Input('cell-pitch-x', 'value'),
     Input('cell-pitch-y', 'value'),
     Input('planes-list', 'value'),
     Input('material-dropdown', 'value'),
     Input('colors-dropdown', 'value')],
)
def create_cell(pitch_x, pitch_y, planes, materials, colors):
    try:
        planes = [float(plane) for plane in planes.split(',')]
    except:
        pass

    planes.sort()

    edge_x = pitch_x
    edge_y = pitch_y
    visible_edge_x = planes[-1] + 0.1 * planes[-1]
    visible_edge_y = planes[-1] + 0.1 * planes[-1]

    x = np.linspace(-edge_x, edge_x, 250)
    y = np.linspace(-edge_y, edge_y, 250)

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
            # Check if water hole
            if planes == [0]:
                if materials is None:
                    text_row.append('Hole Region')
                else:
                    text_row.append(materials[0])

                # For Color
                if colors is not None:
                    row.append(values[0])
                else:
                    row.append(0)

            else:
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
                    if -visible_edge_x < i < visible_edge_x and -visible_edge_y < j < visible_edge_y:
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
                         opacity=0.6,
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
                             range=[-visible_edge_x, visible_edge_x]),
                  yaxis=dict(fixedrange=True,
                             range=[-visible_edge_y, visible_edge_y]),
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
     State('cell-pitch-x', 'value'),
     State('cell-pitch-y', 'value'),
     State('cell-height', 'value'),
     State('material-dropdown', 'value'),
     State('colors-dropdown', 'value'),
     State('cell-stores', 'data')]
)
def store_cell(clicks, name, planes, x_pitch, y_pitch, height, materials, colors, cell_data):
    if clicks is None:
        raise PreventUpdate

    cell_data = cell_data or {}

    planes = [float(plane) for plane in planes.split(',')]
    planes.sort()

    if name is None:
        print("Must enter a cell name")

    elif planes is None:
        print("Must have at least one plane")

    elif x_pitch is None or y_pitch is None:
        print("Must enter a cell pitch")

    elif materials is None:
        print("Must have at least one material")

    elif len(materials) != len(planes) + 1 and planes != [0]:
        print("Material/Radial Planes requirement mismatch")

    else:
        cell_data.update({'{}'.format(name): {'x-pitch': x_pitch,
                                              'y-pitch': y_pitch,
                                              'height': height,
                                              'radii': planes,
                                              'materials': materials,
                                              'colors': colors}})

        return cell_data


#######################################################################################################################
# Assemblies

@app.callback(
    Output('cell-dropdown', 'options'),
    [Input('cell-stores', 'modified_timestamp')],
    [State('cell-stores', 'data')]
)
def populate_dropdown(timestamp, data):
    if timestamp is None:
        raise PreventUpdate

    if data:
        labels = data.keys()
        options = [{'label': label, 'value': label} for label in labels]

        return options


@app.callback(
    Output('injection-cell', 'options'),
    [Input('cell-stores', 'modified_timestamp'),
     Input('cell-dropdown', 'value')],
    [State('cell-stores', 'data')]
)
def populate_dropdown(timestamp, main_cell, data):
    if timestamp is None:
        raise PreventUpdate

    if data:
        labels = data.keys()
        options = [{'label': label, 'value': label} for label in labels]
        if {'label': main_cell, 'value': main_cell} in options:
            options.remove({'label': main_cell, 'value': main_cell})

        return options


@app.callback(
    Output('display-selected', 'children'),
    [Input('assembly-graph', 'selectedData'),
     Input('submit-selected-btn', 'n_clicks')]
)
def display_selected_cells(selectedData, clicks):
    if selectedData:
        xs = [point['x'] for point in selectedData['points']]
        ys = [point['y'] for point in selectedData['points']]
        selected_cell = list(zip(xs, ys))

        return html.P('{}'.format(str(selected_cell)))


@app.callback(
    Output('temp-assembly-stores', 'data'),
    [Input('submit-selected-btn', 'n_clicks'),
     Input('cell-dropdown', 'value'),
     Input('assembly-x-number', 'value'),
     Input('assembly-y-number', 'value')],
    [State('injection-cell', 'value'),
     State('assembly-graph', 'selectedData'),
     State('cell-stores', 'data'),
     State('temp-assembly-stores', 'data')]
)
def configure_stores(clicks, main_cell, assembly_num_x, assembly_num_y, selected_cell,
                     selectedData, cell_data, data):
    data = data or {'main-cell': {}, 'injected-cells': {}, 'assembly-metrics': {}}
    cells = data['injected-cells']

    if main_cell:
        data['main-cell'] = main_cell
        data['assembly-metrics']['assembly-num-x'] = assembly_num_x
        data['assembly-metrics']['assembly-num-y'] = assembly_num_y
        data['assembly-metrics']['assembly-pitch-x'] = cell_data[main_cell]['x-pitch']
        data['assembly-metrics']['assembly-pitch-y'] = cell_data[main_cell]['y-pitch']

    if selected_cell:
        selection_locs = np.column_stack(([point['x'] for point in selectedData['points']],
                                          [point['y'] for point in selectedData['points']]))

        # If there is no entry at all for selections of specified cell type
        if selected_cell not in cells.keys():
            cells.update({'{}'.format(selected_cell): {'indices': selection_locs}})

        # Else need to loop thru indices of existing cell types to check duplicated indices
        cells[selected_cell]['indices'] = selection_locs

        for k in range(len(cells[selected_cell]['indices'])):
            # If the indices are in any of the cells not selected
            cells_list = list(cells.keys())
            for i in range(len(cells_list)):
                if selected_cell != cells_list[i]:

                    if cells[selected_cell]['indices'][k] in cells[cells_list[i]]['indices']:
                        # Remove those indices from that cell
                        cells[cells_list[i]]['indices'].remove(cells[selected_cell]['indices'][k])

    return data


@app.callback(
    Output('assembly-graph', 'figure'),
    [Input('cell-stores', 'data'),
     Input('temp-assembly-stores', 'modified_timestamp')],
    [State('temp-assembly-stores', 'data')],
)
def fill_assembly(cell_data, timestamp, assembly_data):
    main_cell = assembly_data['main-cell'] if assembly_data else None

    if cell_data and main_cell:
        assembly_num_x = assembly_data['assembly-metrics']['assembly-num-x']
        assembly_num_y = assembly_data['assembly-metrics']['assembly-num-y']

        pitch_x = assembly_data['assembly-metrics']['assembly-pitch-x']
        pitch_y = assembly_data['assembly-metrics']['assembly-pitch-y']

        # if planes[0] * assembly_num_x > assembly_dim_x or planes[0] * assembly_num_y > assembly_dim_y:
        #     return html.P("Assembly Dimensions and/or Quantities are insensible. You will see this message"
        #                   "if your specifications are causing pins to overlap!")
        # else:

        data = []

        # Add assembly coolant "background" for selection tool
        x_centers, y_centers = np.meshgrid(np.arange(assembly_num_x),
                                           np.arange(assembly_num_y))

        cell_size = 50
        cell_map = list(zip(x_centers.flatten(), y_centers.flatten()))

        for cell_name in assembly_data['injected-cells'].keys():
            indices = np.array(assembly_data['injected-cells'][cell_name]['indices'])

            # Delete Injection indices from background
            for i in range(len(indices)):
                index = (indices[i][0], indices[i][1])
                if index in cell_map:
                    cell_map.remove(index)

            colors = cell_data[cell_name]['colors'][::-1]
            radii = cell_data[cell_name]['radii'][::-1]
            for i in range(len(colors)):
                # Fix Logic -> hard to follow but works
                color = colors[i]
                if i == 0:
                    symbol = 'square'
                    size = cell_size
                    opacity = .5
                else:
                    radius = radii[i - 1]

                    symbol = 'circle'
                    size = radius / pitch_x * cell_size  # pitch y?
                    opacity = 1

                data.append(go.Scatter(x=indices[:, 0],
                                       y=indices[:, 1],
                                       hoverinfo='none',
                                       mode='markers',
                                       marker=dict(symbol=symbol,
                                                   size=size,
                                                   color=color),
                                       opacity=opacity))

        main_colors = cell_data[assembly_data['main-cell']]['colors'][::-1]
        main_radii = cell_data[assembly_data['main-cell']]['radii'][::-1]

        for i in range(len(main_colors)):
            color = main_colors[i]
            if i == 0:
                symbol = 'square'
                size = cell_size
                opacity = .5
            else:
                radius = main_radii[i - 1]

                symbol = 'circle'
                size = radius / pitch_x * cell_size  # pitch y?
                opacity = 1

            data.append(go.Scatter(x=np.array(cell_map)[:, 0],
                                   y=np.array(cell_map)[:, 1],
                                   hoverinfo='none',
                                   mode='markers',
                                   marker=dict(symbol=symbol,
                                               size=size,
                                               color=color),
                                   opacity=opacity))

        layout = dict(
            title='Assembly Depiction',
            height=1000,
            width=1000,
            clickmode='event+select',
            xaxis=dict(
                range=[-.5, assembly_num_x - .5],
                zeroline=False,
                fixedrange=True
            ),
            yaxis=dict(
                range=[-.5, assembly_num_y - .5],
                zeroline=False,
                fixedrange=True
            ),
        )

        figure = dict(data=data, layout=layout)

        return figure


@app.callback(
    Output('assembly-stores', 'data'),
    [Input('store-assembly-btn', 'n_clicks')],
    [State('assembly-name', 'value'),
     State('temp-assembly-stores', 'data'),
     State('assembly-stores', 'data')]
)
def store_to_assemblies(click, assembly_name, assembly_data, all_assembly_data):
    all_assembly_data = all_assembly_data or {}

    if click:
        all_assembly_data.update({'{}'.format(assembly_name): assembly_data})

    return all_assembly_data


#######################################################################################################################
# Full-Core
@app.callback(
    Output('assembly-dropdown', 'options'),
    [Input('assembly-stores', 'data')]
)
def populate_dropdown(assembly_data):
    options = []
    for assembly_name in assembly_data.keys():
        options.append({'label': assembly_name, 'value': assembly_name})
    return options


@app.callback(
    Output('display-assembly-indices', 'children'),
    [Input('core-graph', 'selectedData')],
)
def show_selection_locations(selectedData):
    if selectedData:
        xs = [point['x'] for point in selectedData['points']]
        ys = [point['y'] for point in selectedData['points']]

        new_xs = []
        new_ys = []
        for i in range(len(xs)):
            if type(xs[i]) is int and type(ys[i]) is int:
                new_xs.append(xs[i])
                new_ys.append(ys[i])

        selected_assemblies = list(zip(new_xs, new_ys))

        return html.P('{}'.format(str(selected_assemblies)))


# TODO: Selectable Shapes or absolute marker size
# TODO: Fix Marker Sizes
@app.callback(
    [Output('core-graph', 'figure'),
     Output('core-stores', 'data')],
    [Input('inject-assembly-btn', 'n_clicks'),
     Input('core-x-dim', 'value'),
     Input('core-y-dim', 'value')],
    [State('core-graph', 'selectedData'),
     State('cell-stores', 'data'),
     State('assembly-dropdown', 'value'),
     State('assembly-stores', 'data'),
     State('core-stores', 'data')]
)
def change_selected_assemblies(clicks, core_x_dim, core_y_dim, selectedData, cell_data, assembly_name, assembly_data,
                               core_data):
    core_data = core_data or {'assembly-assignments': {}}
    graph_data = []

    if clicks and selectedData:
        xs = [point['x'] for point in selectedData['points']]
        ys = [point['y'] for point in selectedData['points']]

        selected_locations = []
        for i in range(len(xs)):
            if type(xs[i]) is int and type(ys[i]) is int \
                    and (xs[i], ys[i]) not in selected_locations:
                selected_locations.append((xs[i], ys[i]))

        core_data['assembly-assignments'].update({'{}'.format(assembly_name):
                                                      {'indices': selected_locations}
                                                  })

        assembly_num_x = assembly_data[assembly_name]['assembly-metrics']['assembly-num-x']
        assembly_num_y = assembly_data[assembly_name]['assembly-metrics']['assembly-num-y']
        pitch_x = assembly_data[assembly_name]['assembly-metrics']['assembly-pitch-x']
        pitch_y = assembly_data[assembly_name]['assembly-metrics']['assembly-pitch-y']

        assembly_width = assembly_num_x * pitch_x
        assembly_height = assembly_num_y * pitch_y
        spacing_x = pitch_x / assembly_width * .85  # Factor to squeeze into assembly marker
        spacing_y = pitch_y / assembly_height * .85  # Factor to squeeze into assembly marker

        span_x = np.linspace(-assembly_num_x / 2 * spacing_x, assembly_num_x / 2 * spacing_x, assembly_num_x)
        span_y = np.linspace(-assembly_num_y / 2 * spacing_y, assembly_num_y / 2 * spacing_y, assembly_num_y)
        pin_xs, pin_ys = np.meshgrid(span_x, span_y)
        pin_xs = pin_xs.flatten()
        pin_ys = pin_ys.flatten()

        for index in selected_locations:
            i = index[0]
            j = index[1]
            test_x = i + pin_xs
            test_y = j + pin_ys

            cell_map = list(zip(test_x, test_y))

            for cell_name in assembly_data[assembly_name]['injected-cells'].keys():
                indices = np.array(assembly_data[assembly_name]['injected-cells'][cell_name]['indices'])

                # Delete Injection indices from background
                for i in range(len(indices)):
                    index = (indices[i][0], indices[i][1])
                    if index in cell_map:
                        cell_map.remove(index)

                colors = cell_data[cell_name]['colors'][::-1]
                radii = cell_data[cell_name]['radii'][::-1]
                for i in range(len(colors)):

                    color = colors[i]
                    if i == 0:
                        symbol = 'square'
                        size = 3
                        opacity = .5
                    else:
                        radius = radii[i - 1]
                        symbol = 'circle'
                        size = 2  # pitch y?
                        opacity = 1

                    graph_data.append(go.Scatter(x=indices[:, 0],
                                                 y=indices[:, 1],
                                                 hoverinfo='none',
                                                 mode='markers',
                                                 showlegend=False,
                                                 marker=dict(symbol=symbol,
                                                             size=size,
                                                             color=color),
                                                 opacity=opacity))

            main_colors = cell_data[assembly_data[assembly_name]['main-cell']]['colors'][::-1]
            main_radii = cell_data[assembly_data[assembly_name]['main-cell']]['radii'][::-1]

            for i in range(len(main_colors)):
                color = main_colors[i]
                if i == 0:
                    symbol = 'square'
                    size = 4
                    opacity = .5
                else:
                    radius = main_radii[i - 1]
                    symbol = 'circle'
                    size = 2  # pitch y?
                    opacity = 1

                graph_data.append(go.Scatter(x=np.array(cell_map)[:, 0],
                                             y=np.array(cell_map)[:, 1],
                                             hoverinfo='none',
                                             mode='markers',
                                             showlegend=False,
                                             marker=dict(symbol=symbol,
                                                         size=size,
                                                         color=color),
                                             opacity=opacity))

    x_centers, y_centers = np.meshgrid(np.arange(core_x_dim),
                                       np.arange(core_y_dim))

    squares = go.Scatter(x=x_centers.flatten(),
                         y=y_centers.flatten(),
                         mode='markers',
                         showlegend=False,
                         marker=dict(symbol='square',
                                     size=55,
                                     color='white',
                                     line=dict(
                                         color='black',
                                         width=1
                                     )),
                         hoverinfo='none',
                         opacity=.5
                         )

    graph_data.append(squares)

    layout = dict(
        title='Core Depiction',
        height=1350,
        width=1350,
        xaxis=dict(
            range=[-.5, core_x_dim - .5],
            zeroline=False,
            fixedrange=True,
            ticks='',
            nticks=core_x_dim + 1
        ),
        yaxis=dict(
            range=[-.5, core_y_dim - .5],
            zeroline=False,
            fixedrange=True,
            ticks='',
            nticks=core_y_dim + 1
        ),
    )

    figure = go.Figure(data=graph_data, layout=layout)

    return figure, core_data


@app.callback(
    Output('debug', 'children'),
    [Input('core-stores', 'modified_timestamp')],
    [State('core-stores', 'data')]
)
def show_core_data(timestamp, core_data):
    return html.P('{}'.format(core_data))

#######################################################################################################################
# Root Geometry Selection
@app.callback(
    Output('root-dropdown', 'options'),
    [Input('cell-stores', 'data'),
     Input('assembly-stores', 'data')]
)
def populate_dropdown(cell_data, assembly_data):
    options = []
    if cell_data:
        for cell_name in cell_data.keys():
            options.append({'label': cell_name, 'value': cell_name})

    if assembly_data:
        for assembly_name in assembly_data.keys():
            options.append({'label': assembly_name, 'value': assembly_name})

    return options


#######################################################################################################################
# Boundaries


@app.callback(
    [Output('boundary-range-x', 'value'),
     Output('boundary-range-y', 'value'),
     Output('boundary-range-z', 'value'),
     # Output('boundary-range-x', 'min'),
     # Output('boundary-range-x', 'max'),
     # Output('boundary-range-y', 'min'),
     # Output('boundary-range-y', 'max'),
     # Output('boundary-range-z', 'min'),
     # Output('boundary-range-z', 'max')
     ],
    [Input('root-dropdown', 'value')],
    [State('cell-stores', 'data'),
     State('assembly-stores', 'data')]
)
def set_boundaries(root_geometry, cell_data, assembly_data):
    if root_geometry:
        if root_geometry in cell_data.keys():
            x_upper = cell_data[root_geometry]['x-pitch'] / 2
            x_lower = -x_upper
            y_upper = cell_data[root_geometry]['y-pitch'] / 2
            y_lower = -y_upper
            z_upper = cell_data[root_geometry]['height'] / 2
            z_lower = -z_upper
            return [x_lower, x_upper], \
                   [y_lower, y_upper], \
                   [z_lower, z_upper],
            # x_lower - np.sqrt(-x_lower), x_upper + np.sqrt(x_upper), \
            # y_lower - np.sqrt(-y_lower), y_upper + np.sqrt(y_upper), \
            # z_lower - np.sqrt(-z_lower), z_upper + np.sqrt(z_upper)

        if root_geometry in assembly_data.keys():
            x_upper = assembly_data[root_geometry]['assembly-metrics']['assembly-num-x'] * \
                      assembly_data[root_geometry]['assembly-metrics']['assembly-pitch-x'] / 2
            x_lower = -x_upper

            y_upper = assembly_data[root_geometry]['assembly-metrics']['assembly-num-y'] * \
                      assembly_data[root_geometry]['assembly-metrics']['assembly-pitch-y'] / 2
            y_lower = -y_upper

            z_upper = cell_data[assembly_data[root_geometry]['main-cell']]['height'] / 2
            z_lower = -z_upper

            # Create min/max values with arbitrary relationship to values -> trying sqrt
            return [x_lower, x_upper], \
                   [y_lower, y_upper], \
                   [z_lower, z_upper],
            # x_lower - np.sqrt(-x_lower), x_upper + np.sqrt(x_upper), \
            # y_lower - np.sqrt(-y_lower), y_upper + np.sqrt(y_upper), \
            # z_lower - np.sqrt(-z_lower), z_upper + np.sqrt(z_upper)


###############################################


# Store whole-geometry outer boundary and type
@app.callback(
    Output('geometry-stores', 'data'),
    [Input('submit-geometry-btn', 'n_clicks')],
    [State('root-dropdown', 'value'),
     State('boundary-range-x', 'value'),
     State('boundary-range-y', 'value'),
     State('boundary-range-z', 'value'),
     State('boundary-type-x', 'value'),
     State('boundary-type-y', 'value'),
     State('boundary-type-z', 'value'),
     State('geometry-stores', 'data')])
def store_boundaries(clicks, root_geometry, range_x, range_y, range_z, btype_x, btype_y, btype_z, geometry_data):
    geometry_data = geometry_data or {}
    if clicks:
        min_x = range_x[0]
        max_x = range_x[1]
        min_y = range_y[0]
        max_y = range_y[1]
        min_z = range_z[0]
        max_z = range_z[1]

        geometry_data.update({'root-geometry': root_geometry,
                              'X-min': min_x, 'X-max': max_x, 'X-btype': btype_x,
                              'Y-min': min_y, 'Y-max': max_y, 'Y-btype': btype_y,
                              'Z-min': min_z, 'Z-max': max_z, 'Z-btype': btype_z})

    return geometry_data
