import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, State, Input

import plotly.graph_objs as go

import openmc
import openmc.model
import openmc.mgxs

import numpy as np
import re
import pickle
import redis


# Add Periodic Table Data
element = [['Hydrogen', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Helium'],
           ['Lithium', 'Beryllium', '', '', '', '', '', '', '', '', '', '', 'Boron', 'Carbon', 'Nitrogen', 'Oxygen',
            'Fluorine', 'Neon'],
           ['Sodium', 'Magnesium', '', '', '', '', '', '', '', '', '', '', 'Aluminium', 'Silicon', 'Phosphorus',
            'Sulfur', 'Chlorine', ' Argon'],
           ['Potassium', ' Calcium', ' Scandium', ' Titanium', ' Vanadium', ' Chromium', 'Manganese', 'Iron', 'Cobalt',
            'Nickel', 'Copper', 'Zinc', 'Gallium', 'Germanium', 'Arsenic', 'Selenium', 'Bromine', 'Krypton'],
           ['Rubidium', 'Strontium', 'Yttrium', 'Zirconium', 'Niobium', 'Molybdenum', 'Technetium', 'Ruthenium',
            'Rhodium', 'Palladium', 'Silver', 'Cadmium', 'Indium', 'Tin', 'Antimony', 'Tellurium', 'Iodine', 'Xenon'],
           [' Cesium', ' Barium', '', 'Hafnium', 'Tantalum', 'Tungsten', 'Rhenium', 'Osmium', 'Iridium', 'Platinum',
            'Gold', 'Mercury', 'Thallium', 'Lead', 'Bismuth', 'Polonium', 'Astatine', 'Radon'],
           [' Francium', ' Radium', '', 'Rutherfordium', 'Dubnium', 'Seaborgium', 'Bohrium', 'Hassium', 'Meitnerium',
            'Darmstadtium', 'Roentgenium', 'Copernicium', 'Ununtrium', 'Ununquadium', 'Ununpentium', 'Ununhexium',
            'Ununseptium', 'Ununoctium'],
           ['', '', 'Lanthanum', 'Cerium', 'Praseodymium', 'Neodymium', 'Promethium', 'Samarium', 'Europium',
            'Gadolinium', 'Terbium', 'Dysprosium', 'Holmium', 'Erbium', 'Thulium', 'Ytterbium', 'Lutetium', ''],
           ['', '', 'Actinium', 'Thorium', 'Protactinium', 'Uranium', 'Neptunium', 'Plutonium', 'Americium', 'Curium',
            'Berkelium', 'Californium', 'Einsteinium', 'Fermium', 'Mendelevium', 'Nobelium', 'Lawrencium', ''], ]

symbol = [['H', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'He'],
          ['Li', 'Be', '', '', '', '', '', '', '', '', '', '', 'B', 'C', 'N', 'O', 'F', 'Ne'],
          ['Na', 'Mg', '', '', '', '', '', '', '', '', '', '', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar'],
          ['K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr'],
          ['Rb ', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe'],
          ['Cs', 'Ba', '', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn'],
          ['Fr', 'Ra', '', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Uut', 'Fl', 'Uup', 'Lv', 'Uus',
           'Uuo'],
          ['', '', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', ''],
          ['', '', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', '']]

atomic_number = [['1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '2'],
                 ['3', '4', '', '', '', '', '', '', '', '', '', '', '5', '6', '7', '8', '9', '10'],
                 ['11', '12', '', '', '', '', '', '', '', '', '', '', '13', '14', '15', '16', '17', '18'],
                 ['19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35',
                  '36'],
                 ['37 ', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53',
                  '54'],
                 ['55', '56', '', '72', '73', '74', '75', '76', '77', '78', '79', '80', '81', '82', '83', '84', '85',
                  '86'],
                 ['87', '88', '', '104', '105', '106', '107', '108', '109', '110', '111', '112', '113', '114', '115',
                  '116', '117', '118'],
                 ['', '', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', ''],
                 ['', '', '89', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '100', '101', '102', '103',
                  '']]

atomic_mass = [[1.00794, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, 4.002602],
               [6.941, 9.012182, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, 10.811, 12.0107, 14.0067, 15.9994, 18.9984032,
                20.1797],
               [22.98976928, 24.3050, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, 26.9815386, 28.0855, 30.973762, 32.065,
                35.453, 39.948],
               [39.0983, 40.078, 44.955912, 47.867, 50.9415, 51.9961, 54.938045, 55.845, 58.933195, 58.6934, 63.546,
                65.38, 69.723, 72.64, 74.92160, 78.96, 79.904, 83.798],
               [85.4678, 87.62, 88.90585, 91.224, 92.90638, 95.96, 98, 101.07, 102.90550, 106.42, 107.8682, 112.411,
                114.818, 118.710, 121.760, 127.60, 126.90447, 131.293],
               [132.9054519, 137.327, .0, 178.49, 180.94788, 183.84, 186.207, 190.23, 192.217, 195.084, 196.966569,
                200.59, 204.3833, 207.2, 208.98040, 209, 210, 222],
               [223, 226, .0, 267, 268, 271, 272, 270, 276, 281, 280, 285, 284, 289, 288, 293, 'unknown', 294],
               [.0, .0, 138.90547, 140.116, 140.90765, 144.242, 145, 150.36, 151.964, 157.25, 158.92535, 162.500,
                164.93032, 167.259, 168.93421, 173.054, 174.9668, .0],
               [.0, .0, 227, 232.03806, 231.03588, 238.02891, 237, 244, 243, 247, 247, 251, 252, 257, 258, 259, 262,
                .0], ]

z = [[.8, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, 1.],
     [.1, .2, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .7, .8, .8, .8, .9, 1.],
     [.1, .2, .0, .0, .0, .0, .0, .0, .0, .0, .0, .0, .6, .7, .8, .8, .9, 1],
     [.1, .2, .3, .3, .3, .3, .3, .3, .3, .3, .3, .3, .6, .7, .8, .8, .9, 1.],
     [.1, .2, .3, .3, .3, .3, .3, .3, .3, .3, .3, .3, .6, .6, .7, .7, .9, 1.],
     [.1, .2, .4, .3, .3, .3, .3, .3, .3, .3, .3, .3, .6, .6, .6, .7, .9, 1.],
     [.1, .2, .5, .3, .3, .3, .3, .3, .3, .3, .3, .3, .6, .6, .6, .6, .9, 1.],
     [.0, .0, .4, .4, .4, .4, .4, .4, .4, .4, .4, .4, .4, .4, .4, .4, .4, .0],
     [.0, .0, .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, .0], ]

# Display element name and atomic mass on hover
hover = []
for a in range(len(symbol)):
    hover.append([i + ': ' + j + '<br>' + 'Atomic Mass: ' + str(k) for i, j, k in zip(symbol[a], element[a], atomic_mass[a])])

# Invert Matrices
symbol = symbol[::-1]
atomic_number = atomic_number[::-1]
hover = hover[::-1]
z = z[::-1]

x = np.arange(np.shape(z)[1])
y = np.arange(np.shape(z)[0])

# Set Colorscale
colorscale = [[0.0, 'rgb(255,255,255)'], [.1, 'rgb(87, 27, 103)'],
              [.2, 'rgb(65, 69, 133)'], [.3, 'rgb(55, 96, 139)'],
              [.4, 'rgb(46, 120, 141)'], [.5, 'rgb(41, 145, 139)'],
              [.6, 'rgb(45, 167, 133)'], [.7, 'rgb(74, 189, 115)'],
              [.8, 'rgb(126, 207, 89)'], [.9, 'rgb(189, 216, 88)'],
              [1.0, 'rgb(252, 229, 64)']]

annotations = []
for n in range(np.shape(z)[0]):
    for m in range(np.shape(z)[1]):
        annotations.append(go.layout.Annotation(text=str(symbol[n][m]), x=x[m], y=y[n],
                                xref='x1', yref='y1', showarrow=False,
                                font=dict(family='Courier New',
                                          size=20,
                                          color='black')))

        annotations.append(go.layout.Annotation(text=str(atomic_number[n][m]), x=x[m] + .3, y=y[n] + .3,
                                         xref='x1', yref='y1', showarrow=False,
                                         font=dict(family='Courier New',
                                                   size=15,
                                                   color='black')
                                         ))

heatmap = go.Heatmap(x=x, y=y, z=z, hoverinfo='text', text=hover, colorscale=colorscale, showscale=False, opacity=.5)

data = [heatmap]

periodic_table = go.Figure(data=data)
periodic_table['layout'].update(
    title="Periodic Table of Elements",
    annotations=annotations,
    xaxis=dict(zeroline=False, showgrid=False, showticklabels=False, ticks='',),
    yaxis=dict(zeroline=False, showgrid=False, showticklabels=False, ticks='',),
    width=1250,
    height=750,
    autosize=False
)

app = dash.Dash()
app.config['suppress_callback_exceptions'] = True

#######################################################################################################################

app.layout = html.Div([
    ################################################################################
    # Title
    html.H2('Test Application',
                style={
                    'position': 'relative',
                    'top': '0px',
                    'left': '10px',
                    'font-family': 'Dosis',
                    'display': 'inline',
                    'font-size': '4.0rem',
                    'color': '#4D637F'
                }),
        html.H2('for',
                style={
                    'position': 'relative',
                    'top': '0px',
                    'left': '20px',
                    'font-family': 'Dosis',
                    'display': 'inline',
                    'font-size': '2.0rem',
                    'color': '#4D637F'
                }),
        html.H2('OpenMC Interface',
                style={
                    'position': 'relative',
                    'top': '0px',
                    'left': '27px',
                    'font-family': 'Dosis',
                    'display': 'inline',
                    'font-size': '4.0rem',
                    'color': '#4D637F'
                }),

    ################################################################################
    html.Br(),

    # Periodic Table for Material Selection
    html.Div([
        dcc.Graph(id='periodic-table',
                  figure=periodic_table
                  ),

        # TODO: figure out why html.A components not working/updating and put all of them in button-activated Div
        dcc.Dropdown(id='material-dropdown'),
        html.Button('Add Material', id='add-material-button', n_clicks=0),
        html.Div(id='material-options-container'),
        html.A(id='material-message-update'),

        html.A(id='chosen-element'),
        html.Div(id='composition-option-container'),
        html.A(id='isotope-message-update'),

        html.Button('Create Cell', id='cell-geometry-button', n_clicks=0),
        html.Div(id='cell-geometry-config-container'),

        html.Div(id='assembly-geometry-config-container'),

        html.Button('Set Geometrical Boundaries', id='whole-geometry-button', n_clicks=0),
        html.Div(id='whole-geometry-config-container'),

        html.Button('Create Mesh', id='create-mesh-button', n_clicks=0),
        html.Div(id='mesh-config-container'),
        html.A(id='mesh-message'),

        html.Button('Configure Cross-sections', id='config-xs-button', n_clicks=0),
        html.Div(id='xs-config-container'),

        html.Button('Configure Scoring', id='config-scores-button', n_clicks=0),
        html.Div(id='scores-config-container'),

        html.Button('Configure Run Settings', id='config-settings-button', n_clicks=0),
        html.Div(id='settings-config-container'),
        html.A(id='settings-message'),
        html.Br(),
    ]),

    ################################################################################
    # Loading/Writing XML Files
    html.Div([
    html.Label('Materials XML File Contents'),
    html.Br(),
    dcc.Textarea(id='materials-xml', rows=20, cols=50, placeholder='Write XML contents here and Load to File'
                                                 'or leave blank and Load from File'),
    html.Br(),
    html.Button('Load Material XML File', n_clicks=0, id='load-materials'),
    html.Button('Write Material XML File', n_clicks=0, id='write-materials'),
    html.P(id='material-placeholder'),   # Used as dummy for mandatory Output in decorator

    html.Label('Geometry XML File Contents'),
    html.Br(),
    dcc.Textarea(id='geometry-xml', rows=20, cols=50, placeholder='Write XML contents here and Load to File'
                                                 'or leave blank and Load from File'),
    html.Br(),
    html.Button('Load Geometry XML File', n_clicks=0, id='load-geometry'),
    html.Button('Write Geometry XML File', n_clicks=0, id='write-geometry'),
    html.P(id='geometry-placeholder'),   # Used as dummy for mandatory Output in decorator

    html.Label('Tallies XML File Contents'),
    html.Br(),
    dcc.Textarea(id='tallies-xml', rows=20, cols=50, placeholder='Write XML contents here and Load to File'
                                                 'or leave blank and Load from File'),
    html.Br(),
    html.Button('Load Tallies XML File', n_clicks=0, id='load-tallies'),
    html.Button('Write Tallies XML File', n_clicks=0, id='write-tallies'),
    html.P(id='tallies-placeholder'),   # Used as dummy for mandatory Output in decorator

    html.Label('Settings XML File Contents'),
    html.Br(),
    dcc.Textarea(id='settings-xml', rows=20, cols=50, placeholder='Write XML contents here and Load to File'
                                                 'or leave blank and Load from File'),
    html.Br(),
    html.Button('Load Settings XML File', n_clicks=0, id='load-settings'),
    html.Button('Write Material XML File', n_clicks=0, id='write-settings'),
    html.P(id='settings-placeholder'),   # Used as dummy for mandatory Output in decorator

    html.Label('Plots XML File Contents'),
    html.Br(),
    dcc.Textarea(id='plots-xml', rows=20, cols=50, placeholder='Write XML contents here and Load to File'
                                                 'or leave blank and Load from File'),
    html.Br(),
    html.Button('Load Plot XML File', n_clicks=0, id='load-plots'),
    html.Button('Write Plot XML File', n_clicks=0, id='write-plots'),
    html.P(id='plots-placeholder'),   # Used as dummy for mandatory Output in decorator
        ]),

    ################################################################################

    html.Button('Generate XML Files & Run Simulation', n_clicks=0, id='xml-button'),
    html.Br(),
    dcc.Textarea(id='console-output', rows=40, cols=75, placeholder='Console Output will appear here...', readOnly=True),

    # Graphing UI
    html.Div([
        dcc.Graph(id='graph'),
        dcc.Dropdown(
            id='score-graph-dropdown',
            placeholder="Select a score")
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
# Materials Interface


# Invoke material options
@app.callback(
    Output('material-options-container', 'children'),
    [Input('add-material-button', 'n_clicks')],)
def invoke_material_options(n_clicks):
    if n_clicks == 0:
        return []
    if n_clicks > 0:
        options = html.Div([dcc.Input(id='material-name', placeholder='Enter Material Name', type="text"),
                            dcc.Input(id='material-density', placeholder='Enter Material Density', type='number'),
                            dcc.Input(id='material-temperature', placeholder='Enter Material Temperature', type='number'),
                            html.Button('Submit Material', id='submit-material-button', n_clicks=0),
                            html.Br()
                            ])
        return options


# Submit material to model
MATERIALS = []
store_object('material-list', MATERIALS)

@app.callback(
    Output('material-dropdown', 'options'),
    [Input('submit-material-button', 'n_clicks')],
    [State('material-name', 'value'),
     State('material-density', 'value'),
     State('material-temperature', 'value'),
     State('material-dropdown', 'options')])
def submit_material(n_clicks, material_name, material_density, material_temperature, material_options):
    MODEL = restore_object('model')
    MATERIALS = restore_object('material-list')

    if n_clicks > 0:
        material = openmc.Material(name=material_name)
        material.set_density('g/cm3', material_density)
        material.temperature = material_temperature

        MODEL.materials.append(material)
        MATERIALS.append(material_name)
        store_object('model', MODEL)
        store_object('material-list', MATERIALS)

        print(MODEL.materials)

        if material_options is not None:
            material_options.append({'label': material_name, 'value': len(material_options)+1})
        if material_options is None:
            material_options = [{'label': material_name, 'value': 0}]

        n_clicks = 0
        return material_options


# Invoke isotope/element options
@app.callback(
    Output('composition-option-container', 'children'),
    [Input('submit-material-button', 'n_clicks')])
def invoke_isotope_options(n_clicks):
    if n_clicks > 0:
        options = html.Div([dcc.Input(id='atomic-mass', placeholder='Enter Atomic Mass'),
                            dcc.RadioItems(id='composition-option',
                                           options=[{'label': 'Atom Percent', 'value': 'atom-percent'},
                                                    {'label': 'Weight Percent', 'value': 'weight-percent'}]),
                            dcc.Input(id='composition-percent', placeholder='Enter Composition Percent'),
                            html.Button('Submit Element/Isotope', id='submit-isotope-button', n_clicks=0)])
        return options


@app.callback(
    Output('chosen-element', 'children'),
    [Input('periodic-table', 'clickData')],
    )
def choose_element(clickData):
    if clickData is not None:
        if 'points' in clickData:
                    point = clickData['points'][0]
                    if 'text' in point:
                        element = point['text']
                        message = '{} has been selected'.format(element)
                        return message
        # return str(clickData)

    else:
        message = 'Please choose element from periodic table'
        return message


# Submit element/isotope to material in model
@app.callback(
    Output('isotope-message-update', 'children'),
    [Input('submit-isotope-button', 'n_clicks')],
    [State('material-dropdown', 'value'),
     State('chosen-element', 'children'),
     State('isotope-info', 'value'),
     State('composition-option', 'value'),
     State('percent-composition', 'value')])
def submit_isotope(n_clicks, selected_material, chosen_element, isotope_info, composition_option, percent_composition):
    MODEL = restore_object('model')

    if n_clicks > 0:
        chosen_element = chosen_element.split(':')[0]
        if isotope_info is not None:
            isotope_str = str(chosen_element) + str(isotope_info)

            if composition_option == 'atom-percent':
                MODEL.materials[selected_material].add_nuclide(isotope_str, percent_composition, 'ao')

            if composition_option == 'weight-percent':
                MODEL.materials[selected_material].add_nuclide(isotope_str, percent_composition, 'wo')

            store_object('model', MODEL)

            message = '{} has been added to {}'.format(isotope_str, selected_material)

        else:
            element_str = str(chosen_element)
            MODEL.materials[selected_material].add_element(element_str, 1)      # TODO: Figure out second argument

            store_object('model', MODEL)

            message = '{} has been added to {}'.format(element_str, selected_material)

        n_clicks = 0
        return message


#######################################################################################################################
# Geometry Interface
store_object('root-cell', openmc.Cell(name='Root cell'))

# Globally store all cell universes
store_object('cell-universes', [])

# Globally store all assembly universes
store_object('assembly-universes', [])


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


#######################################################################################################################
@app.callback(
    Output('click-register-1', 'children'),
    [Input('cell-graph-1', 'clickData')])
def click_register_function_1(clickData):
    region = 0
    click_x = 0
    click_y = 0
    if clickData is not None:
        if 'points' in clickData:
            point = clickData['points'][0]
            if 'text' in point:
                region = int(re.search(r'\d+', point['text']).group())
            if 'x' in point:
                click_x = point['x']
            if 'y' in point:
                click_y = point['y']
        return [region, click_x, click_y]


# Fill Region
# Consider callbacks that correspond to figure attributes -> "An output can only have a single callback function."
store_object('cell-fillings', [])   # TODO: Fix so that different filling combinations can be made
@app.callback(
    Output('cell-graph-1', 'figure'),
    [Input('planes-list-1', 'value'),
     Input('fill-region-button-1', 'n_clicks')],
    [State('material-dropdown', 'value'),
     State('cell-graph-1', 'clickData')]
)
def fill_region_1(planes, n_clicks, selected_material, clickData):
    MODEL = restore_object('model')
    MATERIALS = restore_object('material-list')

    if selected_material == None:
        print("Please select material from dropdown")

    planes = [float(plane) for plane in planes.split(',')]
    planes.sort()

    edge = planes[-1]
    x = np.linspace(-edge, edge, 250)
    y = np.linspace(-edge, edge, 250)

    regions = []
    cell_hover = []
    # Normal Display
    for i in x:
        row = []
        text_row = []
        for j in y:

            if np.sqrt(i ** 2 + j ** 2) < planes[0]:
                row.append(100)      # <- Arbitrary number to adjust color
                text_row.append('Region 1')

            if np.sqrt(i ** 2 + j ** 2) > planes[-1]:
                row.append(75)      # <- Arbitrary number to adjust color
                text_row.append('Region {}'.format(len(planes) + 1))

            for k in range(len(planes) - 1):
                if planes[k] < np.sqrt(i ** 2 + j ** 2) < planes[k + 1]:
                    row.append(k*3)  # <- Arbitrary number to adjust color
                    text_row.append('Region {}'.format(k + 2))
        regions.append(row)
        cell_hover.append(text_row)

    ######################################################
    # Fill region in OpenMC
    outer_radii = []
    for plane in planes:
        outer_radii.append(openmc.ZCylinder(x0=0, y0=0, R=plane, name='{} Outer Radius'))

    print(outer_radii)

    # Initialize region
    click_x = 0
    click_y = 0
    if clickData is not None:
        if 'points' in clickData:
            point = clickData['points'][0]
            if 'x' in point:
                click_x = point['x']
            if 'y' in point:
                click_y = point['y']

        store_object('model', MODEL)    # TODO: Prolly dont need this

        new_hover = []

        if n_clicks > 0:
            CELL_FILLINGS = restore_object('cell-fillings')

            # Change graph on Click # TODO: Figure out why new text wont show up
            if 0 < np.sqrt(click_x ** 2 + click_y ** 2) < planes[0]:
                cell_filling = openmc.Cell(name='{}'.format(MATERIALS[selected_material]),
                                           fill=MODEL.materials[selected_material],
                                           region=-outer_radii[0])
                CELL_FILLINGS.append(cell_filling)
                store_object('cell-fillings', CELL_FILLINGS)

                for row_ in cell_hover:
                    for text in row_:
                        new_hover.append(text.replace('Region 1', '{} Region'.format(MATERIALS[selected_material])))

            if np.sqrt(click_x ** 2 + click_y ** 2) > planes[-1]:
                cell_filling = openmc.Cell(name='{}'.format(MATERIALS[selected_material]),
                                           fill=MODEL.materials[selected_material],
                                           region=+outer_radii[-1])
                CELL_FILLINGS.append(cell_filling)
                store_object('cell-fillings', CELL_FILLINGS)

                for row_ in cell_hover:
                    for text in row_:
                        new_hover.append(text.replace('Region {}'.format(len(planes) + 1),
                                                      '{} Region'.format(MATERIALS[selected_material])))

            for k in range(len(planes) - 1):
                if planes[k] < np.sqrt(click_x ** 2 + click_y ** 2) < planes[k + 1]:
                    cell_filling = openmc.Cell(name='{}'.format(MATERIALS[selected_material]),
                                               fill=MODEL.materials[selected_material],
                                               region=+outer_radii[k] & -outer_radii[k + 1])
                    CELL_FILLINGS.append(cell_filling)
                    store_object('cell-fillings', CELL_FILLINGS)

                    for row_ in cell_hover:
                        for text in row_:
                            new_hover.append(text.replace('Region {}'.format(k + 2),
                                                          '{} Region'.format(MATERIALS[selected_material])))

            n_clicks = 0

        cell_hover = new_hover

    CELL_FILLINGS = restore_object('cell-fillings')
    print(CELL_FILLINGS)

    cell_universe = openmc.Universe(name='{} Cell'.format(MATERIALS[selected_material]))
    cell_universe.add_cells(CELL_FILLINGS)
    print(cell_universe)

    # # Add completely filled cell universe to list of universes
    if len(CELL_FILLINGS) == len(planes)+1:
        CELL_UNIVERSES = restore_object('cell-universes')
        CELL_UNIVERSES.append(cell_universe)
        store_object('cell-universes', CELL_UNIVERSES)

    ######################################################

    heatmap = go.Heatmap(z=regions,
                         x=x,
                         y=y,
                         hoverinfo='x+y+text',
                         text=cell_hover,
                         opacity=0.5,
                         showscale=False)

    data = [heatmap]
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
                  height=1000,
                  width=1000,
                  shapes=shapes)

    figure = dict(data=data, layout=layout)

    return figure


#######################################################################################################################

# Invoke assembly geometry options
@app.callback(
    Output('assembly-geometry-config-container', 'children'),
    [Input('assembly-geometry-button', 'n_clicks')],)
def invoke_assembly_geometry_options(n_clicks):
    if n_clicks > 0:
        options = html.Div([
            html.Br(),
            dcc.Graph(id='assembly-graph'),
            dcc.Dropdown(id='full-assembly-dropdown',),
            dcc.Input(id='assembly-x-dimension', placeholder='Enter assembly x-width dimension',
                      type='number', value=25),
            dcc.Input(id='assembly-y-dimension', placeholder='Enter assembly y-width dimension',
                      type='number', value=25),
            dcc.Input(id='assembly-x-number', placeholder='Enter fuel pins in x-dimension',
                      type='number', value=17),
            dcc.Input(id='assembly-y-number', placeholder='Enter fuel pins in y-dimension',
                      type='number', value=17),
            html.Br(),
          ])
        return options


# TODO: Create dropdown that supplies the planes_list from selected cell geometry
# Fill Assembly
store_object('assemblies', [])
store_object('selected-cells', [])
store_object('all-shapes', [])
@app.callback(
    Output('assembly-graph', 'figure'),
    [Input('assembly-x-dimension', 'value'),
     Input('assembly-y-dimension', 'value'),
     Input('assembly-x-number', 'value'),
     Input('assembly-y-number', 'value'),
     Input('planes-list-1', 'value'),
     Input('assembly-graph', 'clickData')
     # Input('full-assembly-dropdown', 'value'),
     ]
)
def fill_assembly(assembly_dim_x, assembly_dim_y, assembly_num_x, assembly_num_y, planes, clickData):

    planes = [float(plane) for plane in planes.split(',')]
    planes.sort()
    planes = planes[::-1]

    pitch_x = assembly_dim_x/assembly_num_x
    pitch_y = assembly_dim_y/assembly_num_y

    # TODO, if dimensions and quanitities are insensible, limit and explain to user
    # if planes[0]*assembly_num_x > assembly_dim_x \
    #     or planes[0]*assembly_num_y > assembly_dim_y:
    #         assembly_dim_x = planes[0]*assembly_num_x
    #         assembly_dim_y = planes[0]*assembly_num_y

    assembly_region = np.ones((assembly_num_y, assembly_num_x))

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
    SHAPES = restore_object('all-shapes')
    for outer in planes:
        # TODO: make color match that from fill_region
        color = 'rgb({}, {}, {}'.format(outer*255, outer*255, outer*255)
        for a in range(assembly_num_y):
            for b in range(assembly_num_x):
                shape = {
                    # TODO: circles become elliptical with non-symmetric assembly dimensions; FIX
                    'type': 'circle',
                    'x0': b - outer/pitch_x / 2,
                    'y0': a - outer/pitch_y / 2,
                    'x1': b - outer/pitch_x / 2 + outer/pitch_x,
                    'y1': a - outer/pitch_y / 2 + outer/pitch_y,
                    'fillcolor': color,
                    'opacity': .5
                }

                SHAPES.append(shape)
                shapes.append(shape)
                store_object('all-shapes', SHAPES)

    SELECTED_CELLS = restore_object('selected-cells')
    SHAPES = restore_object('all-shapes')

    click_x = click_y = None
    if clickData is not None:
        if 'points' in clickData:
            point = clickData['points'][0]

            if 'x' in point:
                click_x = point['x']
            if 'y' in point:
                click_y = point['y']

        if (click_x, click_y) not in SELECTED_CELLS:
            SELECTED_CELLS.append((click_x, click_y))
            # shapes = SHAPES.remove(SHAPES[click_x][click_y]) # TODO: shapes must be requested: SHAPES[outer][a][b] = SHAPES[math][click_x][click_y]
            store_object('selected-cells', SELECTED_CELLS)

        else:
            SELECTED_CELLS.remove((click_x, click_y))
            # shapes = SHAPES.append(SHAPES[click_x][click_y]) # TODO: shapes must be requested: SHAPES[outer][a][b] = SHAPES[math][click_x][click_y]
            store_object('selected-cells', SELECTED_CELLS)

    print(SELECTED_CELLS)

    layout = dict(
        title='Assembly Depiction',
        height=1000,
        width=1000,

        xaxis=dict(
            range=[-(planes[0]/2 + (pitch_x-planes[0])/2), assembly_num_x],  # pitch_x*assembly_num_x
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            range=[-(planes[0] / 2 + (pitch_y - planes[0]) / 2), assembly_num_y],
            showgrid=False,
            zeroline=False
        ),
        shapes=shapes,
    )

    heatmap = go.Heatmap(z=assembly_region,
                         hoverinfo='x+y+text',
                         text=assembly_hover,
                         opacity=0.5)
    data = [heatmap]

    figure = dict(data=data, layout=layout)

    # OpenMC Assembly Handling
    assembly = openmc.RectLattice(name='')
    assembly.pitch = (pitch_x, pitch_y)
    assembly.lower_left = (-assembly_dim_x / 2, -assembly_dim_y / 2)
    # print(assembly)

    # ASSEMBLIES = restore_object('assemblies')
    # ASSEMBLIES = ASSEMBLIES.append(assembly)
    # store_object('assemblies', ASSEMBLIES)

    # TODO: Fill Assembly in OpenMC
    # assembly.universes = np.tile(fuel_pin_universe, (x_dim, y_dim))
    # assembly.universes[template_x, template_y] = guide_tube_universe

    # TODO: Make sure that not a bunch of universes are appended for each change in input
    # Append to assembly universe to assembly universes list
    # assembly_universes.append(assembly)
    # assembly_bounds.append([assembly.lower_left])

    return figure

###################################


# Invoke Geometrical Boundary Options
@app.callback(
    Output('whole-geometry-config-container', 'children'),
    [Input('whole-geometry-button', 'n_clicks')],)
def invoke_whole_geometry_options(n_clicks):
    if n_clicks > 0:
        options = html.Div([html.A('Pick root geometry from Dropdown'),
                            dcc.Dropdown(id='root-cell-option'),
                            html.Br(),
                            dcc.RangeSlider(id='boundary-range-x',
                                            min=-1000,
                                            max=1000,
                                            value=[-20, 20],
                                            marks={
                                                -1000: {'label': '-1000', 'style': {'color': '#77b0b1'}},
                                                0: {'label': '0', 'style': {'color': '#f50'}},
                                                1000: {'label': '1000', 'style': {'color': '#f50'}}
                                            },
                                            allowCross=False),
                            html.Br(),
                            dcc.RadioItems(id='boundary-type-x',
                                           options=[
                                                {'label': 'Reflective', 'value': 'reflective'},
                                                {'label': 'Vacuum', 'value': 'vacuum'},
                                            ],
                                           value='vacuum'
                                           ),
                            html.Br(),
                            dcc.RangeSlider(id='boundary-range-y',
                                            min=-1000,
                                            max=1000,
                                            value=[-20, 20],
                                            marks={
                                                -1000: {'label': '-1000', 'style': {'color': '#77b0b1'}},
                                                0: {'label': '0', 'style': {'color': '#f50'}},
                                                1000: {'label': '1000', 'style': {'color': '#f50'}}
                                            },
                                            allowCross=False),
                            html.Br(),
                            dcc.RadioItems(id='boundary-type-y',
                                           options=[
                                               {'label': 'Reflective', 'value': 'reflective'},
                                               {'label': 'Vacuum', 'value': 'vacuum'},
                                           ],
                                           value='vacuum'
                                           ),
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
                                            allowCross=False),
                            html.Br(),
                            dcc.RadioItems(id='boundary-type-z',
                                           options=[
                                               {'label': 'Reflective', 'value': 'reflective'},
                                               {'label': 'Vacuum', 'value': 'vacuum'},
                                           ],
                                           value='vacuum'
                                           ),
                            html.Br()])

        return options


@app.callback(
    Output('root-cell-option', 'options'),
)
def root_cell_fill():   # Goes through cells first, then assemblies
    options = []
    for universe in range(len(all_universes)):
        options.append(
            {'label': all_universes[universe].name, 'value': universe}
        )
    return options

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


# Set whole-geometry outer boundary and type
@app.callback(
    Output('geometry-boundary-placeholder', 'value'),                       # TODO: Offer 2 different planes: cylindrical and box
    [Input('boundary-range-x', 'value'),
     Input('boundary-range-y', 'value'),
     Input('boundary-range-z', 'value'),
     Input('boundary-type-x', 'value'),
     Input('boundary-type-y', 'value'),
     Input('boundary-type-z', 'value')])
def set_boundaries(range_x, range_y, range_z, btype_x, btype_y, btype_z):   # TODO: Allow different boundary types for any surface
    min_x = openmc.XPlane(x0=range_x[0], boundary_type=btype_x)
    max_x = openmc.XPlane(x0=range_x[1], boundary_type=btype_x)
    min_y = openmc.YPlane(y0=range_y[0], boundary_type=btype_y)
    max_y = openmc.YPlane(y0=range_y[1], boundary_type=btype_y)
    min_z = openmc.ZPlane(z0=range_z[0], boundary_type=btype_z)
    max_z = openmc.ZPlane(z0=range_z[1], boundary_type=btype_z)
    root_cell.region = +min_x & -max_x & \
                       +min_y & -max_y & \
                       +min_z & -max_z
    return


# TODO: When simulation is run, fill the root cell with value from dropdown i.e.
# root_cell.fill = all_universes[dropdown_value]

# Create root Universe
# restore_object('model').geometry.root_universe = openmc.Universe(name='Root Universe')
# restore_object('model').geometry.root_universe.add_cell(root_cell)

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


############################################################################################################
# # Cross-Section Interface
# mgxs_lib = openmc.mgxs.Library(restore_object('model').geometry)
#
#
# @app.callback(
#     Output('xs-config-container', 'children'),
#     [Input('config-xs-button', 'n_clicks')],)
# def invoke_xs_options(n_clicks):
#     if n_clicks > 0:
#         options = html.Div([
#                             html.Label('Number of Energy Groups'),
#                             html.Br(),
#                             dcc.Slider(
#                                 id='energy-group-input',
#                                 min=0,
#                                 max=100,
#                                 step=1,
#                                 value=5,
#                                 marks={i: i for i in range(0, 100, 5)},
#                             ),
#                            html.Br(),
#                            html.Label('Select mesh to apply to cross-section calculations'),
#                            html.A(id='cross-section-message'),
#         ])
#
#         return options
#
#
# # TODO: import mesh into function
# @app.callback(
#     Output('cross-section-message', 'children'),
#     [Input('energy-group-input', 'value'),
#      Input('mesh-dropdown', 'value')],
# )
# def build_xs_library(groups, meshes):
#     energy_groups = openmc.mgxs.EnergyGroups()
#     # TODO: Make sure the groups+1 is accurate
#     energy_groups.group_edges = np.logspace(-3, 7.3, groups+1)
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
#
#
# ############################################################################################################
# # Tallies Interface
# restore_object('model').tallies = openmc.Tallies()
#
#
# @app.callback(
#     Output('scores-config-container', 'children'),
#     [Input('config-scores-button', 'n_clicks')],)
# def invoke_scores_options(n_clicks):
#     if n_clicks > 0:
#         options = html.Div([
#                            html.Label('Select mesh filters for scoring'),
#                            dcc.Dropdown(id='mesh-filters-dropdown',
#                                         multi=True),
#                            html.Label('Desired Scores'),
#                            # TODO: Add the rest of the scores
#                            dcc.Checklist(
#                                id='scores-checklist',
#                                options=[
#                                    {'label': 'Flux  ', 'value': 'flux'},
#
#                                    {'label': 'Absorption  ', 'value': 'absorption'},
#                                    {'label': 'Elastic   ', 'value': 'elastic'},
#                                    {'label': 'Fission  ', 'value': 'fission'},
#                                    {'label': 'Scatter  ', 'value': 'scatter'},
#                                    {'label': 'Total  ', 'value': 'total'},
#
#                                    {'label': 'Current  ', 'value': 'current'},
#                                    {'label': 'Decay Rate  ', 'value': 'decay-rate'},
#
#                                ],
#                                values=['flux']),
#                            html.A(id='scores-message')
#         ])
#
#         return options
#
#
# @app.callback(
#     Output('mesh-filters-dropdown', 'options'))
# def populate_mesh_filter_dropdown():
#     options = []
#     for mesh_filter in range(len(mesh_filters_list)):
#         # TODO: Make sure this is correct
#         options.append({'label': mesh_filters_list[mesh_filter].name, 'value': mesh_filter})
#
#     return options
#
#
# # TODO: Import mesh_filter/mgxs_lib to function
# @app.callback(
#     Output('scores-message', 'children'),
#     [Input('scores-checklist', 'value'),
#      Input('mesh-filters-dropdown', 'value')]
# )
# def create_tallies(scores, mesh_filters):
#     mgxs_lib.add_to_tallies_file(restore_object('model').tallies, merge=True)
#
#     # TODO: Allow for user specified combination of scores and mesh filters; for now just do everything
#     for score in scores:
#         for filter in range(len(mesh_filters)):
#             tally = openmc.Tally(name=score)
#             tally.filters = [mesh_filters[filter]]
#             tally.scores = [score]
#
#             # Add tally to the tallies file
#             restore_object('model').tallies.append(tally)
#
#     # message =
#     return
#
# ############################################################################################################
# # Settings Interface
#
#
# @app.callback(
#     Output('settings-config-container', 'children'),
#     [Input('config-settings-button', 'n_clicks')],)
# def invoke_settings_options(n_clicks):
#     if n_clicks > 0:
#         options = html.Div([
#                         html.Label('Total/Inactive Batches for Simulation'),
#                         dcc.RangeSlider(
#                             id='total-inactive-batches',
#                             min=0,
#                             max=100,
#                             value=[5, 10],
#                             marks={i: i for i in range(0, 100, 5)},
#                             included=False,
#                             pushable=5),
#
#                         html.Br(),
#                         html.Label('Number of Generations per Batch in Simulation'),
#                         dcc.Slider(
#                             id='generations-per-batch',
#                             min=0,
#                             max=100,
#                             step=1,
#                             value=10,
#                             marks={i: i for i in range(0, 100, 5)}
#                         ),
#                         html.Br(),
#                         html.Label('Number of Particles in Simulation'),
#                         dcc.Slider(
#                             id='particles-input',
#                             min=0,
#                             max=10000,
#                             step=1,
#                             value=500,
#                             marks={i: i for i in range(0, 10000, 500)}
#                         ),
#         ])
#
#         return options
#
# # restore_object('model').settings.confidence_intervals = False
# # restore_object('model').settings.cutoff =
# # restore_object('model').settings.eigenvalue
# # restore_object('model').settings.energy_grid =
# # restore_object('model').settings.entropy
# # restore_object('model').settings.fixed_source
# # log_grid_bins # Default: 8000
# # natural_elements = ENDF/B-VII.0 or JENDL-4.0
# # restore_object('model').settings.no_reduce = True
# # restore_object('model').settings.output.cross_sections = False
# # restore_object('model').settings.output.summary = False
# # restore_object('model').settings.output.tallies = True
# # restore_object('model').settings.ptables = True
# # restore_object('model').settings.run_cmfd = False
# # restore_object('model').settings.seed = 1
# # restore_object('model').settings.source
# # restore_object('model').settings.state_point
# # restore_object('model').settings.source_point
# # restore_object('model').settings.survival_biasing
# # restore_object('model').settings.threads
# # restore_object('model').settings.trace
# # restore_object('model').settings.track
# # restore_object('model').settings.trigger
# # restore_object('model').settings.uniform_fs
# # restore_object('model').settings.verbosity = 10
# # Resonance Scattering
#
#
# @app.callback(
#     Output('settings-message', 'children'),
#     [Input('total-inactive-batches', 'value'),
#      Input('generations-per-batch', 'value'),
#      Input('particles-input', 'value'),
#      Input('boundary-range-x', 'value'),
#      Input('boundary-range-y', 'value'),
#      Input('boundary-range-z', 'value')]
#     )
# def apply_settings(total_batches, inactive_batches, generations_per_batch, particles, range_x, range_y, range_z):
#     # Make sure this works
#     restore_object('model').settings.cross_sections = '/cross-sections/cross_sections.xml'
#     restore_object('model').settings.batches = total_batches
#     restore_object('model').settings.inactive = inactive_batches
#     restore_object('model').settings.generations_per_batch = generations_per_batch
#     restore_object('model').settings.particles = particles
#     restore_object('model').settings.source = openmc.Source(space=openmc.stats.Box(
#         [range_x[0], range_y[0], range_z[0]], [range_x[1], range_y[1], range_z[1]],
#         # TODO: See other options for only_fissionable
#         only_fissionable=True))
#     return
#
#
# ############################################################################################################
#
# @app.callback(
#     Output(component_id='console-output', component_property='value'),
#     [Input(component_id='xml-button', component_property='n_clicks')],)
# def run_model(run_click):
#     if int(run_click) > 0:
#
#         restore_object('model').export_to_xml()
#
#         xml_files = glob('*.xml')
#         print(xml_files)
#
#         pass_test = False
#         while not pass_test:
#             bool_array = []
#             for file in range(len(xml_files)):
#                 exists = os.path.exists(xml_files[file])
#                 if exists:
#                     bool_array.append(exists)
#
#             if np.array(bool_array).all():
#                 pass_test = True
#                 print('All files exist')
#
#             time.sleep(1)
#
#         output = io.StringIO()
#         with redirect_stdout(output):
#             openmc.run()
#
#         run_click = 0
#
#         return output.getvalue()
#
#
# #######################################################################################################################
# # Load XML from File
# @app.callback(
#     Output(component_id='materials-xml', component_property='value'),
#     [Input(component_id='load-materials', component_property='n_clicks')],
# )
# def show_material_xml_contents(run_click):
#     if run_click > 0:
#         filename = 'materials.xml'
#         contents = open(filename).read()
#         run_click = 0
#         return contents
#
#
# @app.callback(
#     Output(component_id='geometry-xml', component_property='value'),
#     [Input(component_id='load-geometry', component_property='n_clicks')],
# )
# def show_material_xml_contents(run_click):
#     if run_click > 0:
#         filename = 'geometry.xml'
#         contents = open(filename).read()
#         run_click = 0
#         return contents
#
#
# @app.callback(
#     Output(component_id='tallies-xml', component_property='value'),
#     [Input(component_id='load-tallies', component_property='n_clicks')],
# )
# def show_material_xml_contents(run_click):
#     if run_click > 0:
#         filename = 'tallies.xml'
#         contents = open(filename).read()
#         run_click = 0
#         return contents
#
#
# @app.callback(
#     Output(component_id='settings-xml', component_property='value'),
#     [Input(component_id='load-settings', component_property='n_clicks')],
# )
# def show_material_xml_contents(run_click):
#     if run_click > 0:
#         filename = 'settings.xml'
#         contents = open(filename).read()
#         run_click = 0
#         return contents
#
#
# @app.callback(
#     Output(component_id='plots-xml', component_property='value'),
#     [Input(component_id='load-plots', component_property='n_clicks')],
# )
# def show_material_xml_contents(run_click):
#     if run_click > 0:
#         filename = 'plots.xml'
#         contents = open(filename).read()
#         run_click = 0
#         return contents
#
#
# #######################################################################################################################
# # Write XML to File
# @app.callback(
#     Output(component_id='material-placeholder', component_property='children'),
#     [Input(component_id='write-materials', component_property='n_clicks')],
#     [State(component_id='materials-xml', component_property='value')],
# )
# def write_material_xml_contents(write_click, contents):
#     if write_click > 0:
#         filename = 'materials.xml'
#         file = open(filename, "w+")
#         file.write(contents)
#         file.close()
#         write_click = 0
#
#
# @app.callback(
#     Output(component_id='geometry-placeholder', component_property='children'),
#     [Input(component_id='write-geometry', component_property='n_clicks')],
#     [State(component_id='geometry-xml', component_property='value')],
# )
# def write_material_xml_contents(write_click, contents):
#     if write_click > 0:
#         filename = 'geometry.xml'
#         file = open(filename, "w+")
#         file.write(contents)
#         file.close()
#         write_click = 0
#
#
# @app.callback(
#     Output(component_id='tallies-placeholder', component_property='children'),
#     [Input(component_id='write-tallies', component_property='n_clicks')],
#     [State(component_id='tallies-xml', component_property='value')],
# )
# def write_material_xml_contents(write_click, contents):
#     if write_click > 0:
#         filename = 'tallies.xml'
#         file = open(filename, "w+")
#         file.write(contents)
#         file.close()
#         write_click = 0
#
#
# @app.callback(
#     Output(component_id='settings-placeholder', component_property='children'),
#     [Input(component_id='write-settings', component_property='n_clicks')],
#     [State(component_id='settings-xml', component_property='value')],
# )
# def write_material_xml_contents(write_click, contents):
#     if write_click > 0:
#         filename = 'settings.xml'
#         file = open(filename, "w+")
#         file.write(contents)
#         file.close()
#         write_click = 0
#
#
# @app.callback(
#     Output(component_id='plots-placeholder', component_property='children'),
#     [Input(component_id='write-plots', component_property='n_clicks')],
#     [State(component_id='plots-xml', component_property='value')],
# )
# def write_material_xml_contents(write_click, contents):
#     if write_click > 0:
#         filename = 'plots.xml'
#         file = open(filename, "w+")
#         file.write(contents)
#         file.close()
#         write_click = 0
#
#
# #######################################################################################################################
# # TODO: Take label from checklist and pass to dropdown instead of value only
# @app.callback(
#     Output(component_id='score-graph-dropdown', component_property='options'),
#     [Input(component_id='scores-checklist', component_property='values')],
# )
# def disable_unscored_dropdown(scores):
#     return [{'label': score.title(), 'value': score, 'disabled': False} for score in scores]
#
#
# #######################################################################################################################
#
#
# @app.callback(
#     Output(component_id='graph', component_property='figure'),
#     [Input(component_id='score-graph-dropdown', component_property='value')],
# )
# def statepoint_evaluation(desired_score, ):
#
#     sp = openmc.StatePoint(filename=str(*glob('statepoint*')))
#
#     # Get k_effs for each generation
#     k_effs = sp.k_generation
#
#     # Extract the current tally separately
#     if desired_score == 'current':
#         tally = sp.get_tally(scores=[desired_score])
#         goal = tally.get_slice(scores=[desired_score])
#
#     else:
#         tally = sp.get_tally(scores=[desired_score])
#         goal = tally.get_slice(scores=[desired_score])
#
#     # Initialize MGXS Library with OpenMC statepoint data
#     # xs_lib.load_from_statepoint(sp)
#
#     dims = (10, 17, 17)
#     goal_array = goal.get_values().reshape(dims)
#
#     ##############################################################################################
#     # data = [go.Surface(z=goal_array[0],
#     #                    # zmax=c_max,
#     #                    # zmin=0,
#     #                    colorscale='Viridis',
#     #                    )]
#     ##############################################################################################
#
#     maxes = []
#     for m in range(len(goal_array)):
#         c_max = np.amax(np.array(goal_array[m]))
#         maxes.append(c_max)
#     c_max = np.max(np.array(maxes))
#
#     # Instantiate Data
#     data = [go.Surface(z=goal_array[0],
#                        zmax=c_max,
#                        zmin=0,
#                        colorscale='Viridis',
#                        )]
#
#     ##############################################
#
#     # Instantiate Frames
#     frames = []
#     steps = []
#     for k in range(len(goal_array)):
#         frame_data = go.Surface(z=goal_array[k])
#         frame = dict(data=[frame_data], name='Axial Step {}'.format(k))
#         frames.append(frame)
#
#         slider_step = dict(args=[
#             [str(goal_array[k])],
#             dict(frame=dict(duration=0, redraw=False),
#                  mode='immediate',
#                  transition={'duration': 0})
#         ],
#             label='{} cm'.format(goal_array[k]),
#             method='animate')
#         steps.append(slider_step)
#
#     ##################################################################
#
#     # Slider Control
#     sliders_dict = dict(active=0,                                       # Starting Position
#                         yanchor='top',
#                         xanchor='left',
#                         currentvalue=dict(
#                              font={'size': 20},
#                              prefix='Axial Step:',
#                              visible=True,
#                              xanchor='right'
#                          ),
#                         # Transition for slider button
#                         transition=dict(duration=500,
#                                         easing='cubic-in-out'),
#                         pad={'b': 10, 't': 50},
#                         len=.9,
#                         x=0.1,
#                         y=0,
#                         steps=steps
#                         )
#
#     ##################################################################
#
#     # Layout
#     layout = dict(title='Test',
#                   hovermode='closest',
#                   width=1500,
#                   height=1000,
#                   scene=dict(
#                         zaxis=dict(range=[.01, c_max])),
#                   updatemenus=[dict(type='buttons',
#
#                                     buttons=[dict(args=[None,
#                                                         dict(frame=dict(duration=500,
#                                                                         redraw=False),
#                                                              fromcurrent=True,
#                                                              transition=dict(duration=100,
#                                                                              easing='quadratic-in-out'))],
#                                                   label=u'Play',
#                                                   method=u'animate'
#                                                   ),
#
#                                              # [] around "None" are important!
#                                              dict(args=[[None], dict(frame=dict(duration=0,
#                                                                                 redraw=False),
#                                                                      mode='immediate',
#                                                                      transition=dict(duration=0))],
#                                                   label='Pause',
#                                                   method='animate'
#                                                   )
#                                              ],
#
#                                     # Play Pause Button Location & Properties
#                                     direction='left',
#                                     pad={'r': 10, 't': 87},
#                                     showactive=True,
#                                     x=0.1,
#                                     xanchor='right',
#                                     y=0,
#                                     yanchor='top'
#                                     )],
#
#                   slider=dict(args=[
#                                 'slider.value', {
#                                     'duration': 1000,
#                                     'ease': 'cubic-in-out'
#                                 }
#                             ],
#                             # initialValue=burnup[0],           # ???
#                             plotlycommand='animate',
#                             # values=burnup,                    # ???
#                             visible=True
#                         ),
#                   sliders=[sliders_dict]
#                   )
#
#     ##################################################################
#
#     figure = dict(data=data, layout=layout, frames=frames)
#
#     ###################################
#     # trace = go.Scatter(
#     #     x=np.arange(len(k_effs)),
#     #     y=k_effs,
#     #     mode='line'
#     # )
#     # data = [trace]
#     # layout = dict(title='K-effective vs Iteration')
#     # figure = dict(data=data, layout=layout)
#     ###################################
#
#     return figure


if __name__ == '__main__':
    app.run_server(debug=True)
