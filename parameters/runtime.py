import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, State, Input

import openmc
import openmc.model
import openmc.mgxs

import numpy as np
import time
import io
from glob import glob
import os
from shutil import copyfile
from contextlib import redirect_stdout

import json

from app import app

layout = html.Div([

    # Title
    html.H2('Runtime Verification & Model Generation',
            style={
                'position': 'relative',
                'top': '0px',
                'left': '10px',
                'font-family': 'Dosis',
                'display': 'inline',
                'font-size': '4.0rem',
                'color': '#4D637F'
            }), html.Br(),

    #############################################################################
    html.P('Pick root geometry from Dropdown'),
    dcc.Dropdown(id='root-dropdown'),
    html.Button('Generate XML Files', id='xml-button', n_clicks=0),

    # Loading/Writing XML Files
    html.Div([
        dcc.ConfirmDialog(
            id='confirm',
            message='Are you sure you want to write these contents to the file?',
        ),
        html.Div([
            html.Label('Geometry XML File Contents'),
            html.Br(),
            dcc.Textarea(id='geometry-xml', rows=20, cols=50, placeholder='Write XML contents here and Load to File'
                                                                          'or leave blank and Load from File'),
            html.Br(),
            html.Button('Load Geometry XML File', n_clicks=0, id='load-geometry'),
            html.Button('Write Geometry XML File', n_clicks=0, id='write-geometry'),
            html.P(id='geometry-placeholder'),  # Used as dummy for mandatory Output in decorator

            html.Label('Plots XML File Contents'),
            html.Br(),
            dcc.Textarea(id='plots-xml', rows=20, cols=50, placeholder='Write XML contents here and Load to File'
                                                                       'or leave blank and Load from File'),
            html.Br(),
            html.Button('Load Plot XML File', n_clicks=0, id='load-plots'),
            html.Button('Write Plot XML File', n_clicks=0, id='write-plots'),
            html.P(id='plots-placeholder'),  # Used as dummy for mandatory Output in decorator
        ],
            style=dict(
                display='table-cell',
                verticalAlign="top",
                width='30%'
            ),
        ),

        html.Div([
            html.Label('Materials XML File Contents'),
            html.Br(),
            dcc.Textarea(id='materials-xml', rows=20, cols=50, placeholder='Write XML contents here and Load to File'
                                                                           'or leave blank and Load from File'),
            html.Br(),
            html.Button('Load Material XML File', n_clicks=0, id='load-materials'),
            html.Button('Write Material XML File', n_clicks=0, id='write-materials'),
            html.P(id='material-placeholder'),  # Used as dummy for mandatory Output in decorator

            html.Div(style=dict(height=250)),

            html.Div(id='memory-display'),
            html.Button('Run Simulation', id='run-button', n_clicks=0),
            html.Br(),
            dcc.Textarea(id='console-output', rows=40, cols=75, placeholder='Console Output will appear here...',
                         readOnly=True),
        ],
            style=dict(
                width='30%',
                display='table-cell',
                verticalAlign="top",
            ),
        ),

        html.Div([
            html.Label('Tallies XML File Contents'),
            html.Br(),
            dcc.Textarea(id='tallies-xml', rows=20, cols=50, placeholder='Write XML contents here and Load to File'
                                                                         'or leave blank and Load from File'),
            html.Br(),
            html.Button('Load Tallies XML File', n_clicks=0, id='load-tallies'),
            html.Button('Write Tallies XML File', n_clicks=0, id='write-tallies'),
            html.P(id='tallies-placeholder'),  # Used as dummy for mandatory Output in decorator

            html.Label('Settings XML File Contents'),
            html.Br(),
            dcc.Textarea(id='settings-xml', rows=20, cols=50, placeholder='Write XML contents here and Load to File'
                                                                          'or leave blank and Load from File'),
            html.Br(),
            html.Button('Load Settings XML File', n_clicks=0, id='load-settings'),
            html.Button('Write Material XML File', n_clicks=0, id='write-settings'),
            html.P(id='settings-placeholder'),  # Used as dummy for mandatory Output in decorator
        ],
            style=dict(
                width='30%',
                display='table-cell',
                verticalAlign="top",
            ),
        ),
    ], style=dict(
        width='100%',
        display='table',
    ),
    ),
])


############################################################################################################
@app.callback(
Output('root-dropdown', 'options'),
[Input('cell-stores', 'data'),
 Input('assembly-stores', 'data')]
)
def populate_dropdown(cell_data, assembly_data):
    options = []
    for cell_name in cell_data.keys():
        options.append({'label': cell_name, 'value': cell_name})

    for assembly_name in assembly_data.keys():
        options.append({'label': assembly_name, 'value': assembly_name})

    print("Root Dropdown options:", options)
    return options

############################################################################################################


# Load XML from File
@app.callback(
    Output('materials-xml', 'value'),
    [Input('load-materials', 'n_clicks')],
)
def show_material_xml_contents(run_click):
    if run_click > 0:
        script_dir = os.path.dirname(__file__)
        filename = os.path.join(script_dir, '../xml-files/materials.xml')
        contents = open(filename).read()
        return contents


@app.callback(
    Output('geometry-xml', 'value'),
    [Input('load-geometry', 'n_clicks')],
)
def show_material_xml_contents(run_click):
    if run_click > 0:
        script_dir = os.path.dirname(__file__)
        filename = os.path.join(script_dir, '../xml-files/geometry.xml')
        contents = open(filename).read()
        return contents


@app.callback(
    Output('tallies-xml', 'value'),
    [Input('load-tallies', 'n_clicks')],
)
def show_material_xml_contents(run_click):
    if run_click > 0:
        script_dir = os.path.dirname(__file__)
        filename = os.path.join(script_dir, '../xml-files/tallies.xml')
        contents = open(filename).read()
        return contents


@app.callback(
    Output('settings-xml', 'value'),
    [Input('load-settings', 'n_clicks')],
)
def show_material_xml_contents(run_click):
    if run_click > 0:
        script_dir = os.path.dirname(__file__)
        filename = os.path.join(script_dir, '../xml-files/settings.xml')
        contents = open(filename).read()
        return contents


@app.callback(
    Output('plots-xml', 'value'),
    [Input('load-plots', 'n_clicks')],
)
def show_material_xml_contents(run_click):
    if run_click > 0:
        script_dir = os.path.dirname(__file__)
        filename = os.path.join(script_dir, '../xml-files/plots.xml')
        contents = open(filename).read()
        return contents


#######################################################################################################################
# Write XML to File

@app.callback(Output('confirm', 'displayed'),
              [Input('write-materials', 'n_clicks'),
               Input('write-geometry', 'n_clicks'),
               Input('write-tallies', 'n_clicks'),
               Input('write-settings', 'n_clicks'),
               Input('write-plots', 'n_clicks')])
def display_confirm(mat_click, geo_click, tal_click, set_click, plot_click):
    if mat_click or geo_click or tal_click or set_click or plot_click:
        return True
    return False


@app.callback(
    Output('material-placeholder', 'children'),
    [Input('confirm', 'submit_n_clicks')],
    [State('materials-xml', 'value')],
)
def write_material_xml_contents(write_click, contents):
    if write_click:
        script_dir = os.path.dirname(__file__)
        filename = os.path.join(script_dir, '../xml-files/materials.xml')
        file = open(filename, "w+")
        file.write(contents)
        file.close()


@app.callback(
    Output('geometry-placeholder', 'children'),
    [Input('confirm', 'submit_n_clicks')],
    [State('geometry-xml', 'value')],
)
def write_material_xml_contents(write_click, contents):
    if write_click:
        script_dir = os.path.dirname(__file__)
        filename = os.path.join(script_dir, '../xml-files/geometry.xml')
        file = open(filename, "w+")
        file.write(contents)
        file.close()


@app.callback(
    Output('tallies-placeholder', 'children'),
    [Input('confirm', 'submit_n_clicks')],
    [State('tallies-xml', 'value')],
)
def write_material_xml_contents(write_click, contents):
    if write_click:
        script_dir = os.path.dirname(__file__)
        filename = os.path.join(script_dir, '../xml-files/tallies.xml')
        file = open(filename, "w+")
        file.write(contents)
        file.close()


@app.callback(
    Output('settings-placeholder', 'children'),
    [Input('confirm', 'submit_n_clicks')],
    [State('settings-xml', 'value')],
)
def write_material_xml_contents(write_click, contents):
    if write_click:
        script_dir = os.path.dirname(__file__)
        filename = os.path.join(script_dir, '../xml-files/settings.xml')
        file = open(filename, "w+")
        file.write(contents)
        file.close()


@app.callback(
    Output('plots-placeholder', 'children'),
    [Input('confirm', 'submit_n_clicks')],
    [State('plots-xml', 'value')],
)
def write_material_xml_contents(write_click, contents):
    if write_click:
        script_dir = os.path.dirname(__file__)
        filename = os.path.join(script_dir, '../xml-files/plots.xml')
        file = open(filename, "w+")
        file.write(contents)
        file.close()


#######################################################################################################################

@app.callback(
    Output('memory-display', 'children'),
    [Input('xml-button', 'n_clicks')],

    [State('root-dropdown', 'value'),

     State('material-stores', 'data'),

     State('cell-stores', 'data'),
     State('assembly-stores', 'data'),
     State('boundary-stores', 'data'),

     State('mesh-stores', 'data'),

     State('mesh-score-stores', 'data'),

     State('settings-stores', 'data')]
)
def build_model(click, root_geometry, material_data, cell_data, assembly_data, boundary_data, mesh_data, score_data, settings_data):
    if click:
        model = openmc.model.Model()

        print(material_data)
        print(cell_data)
        print(assembly_data)
        print(boundary_data)
        print(score_data)
        print(json.dumps(settings_data, indent=2))

        #######################################
        # Materials

        MATERIALS = openmc.Materials([])
        for material_name in material_data.keys():
            density = material_data[material_name]['density']
            temperature = material_data[material_name]['temperature']

            mat_object = openmc.Material(name=material_name)
            mat_object.set_density('g/cm3', density)
            mat_object.temperature = temperature
            mat_object.depletable = False

            elements = material_data[material_name]['elements']
            masses = material_data[material_name]['masses']
            compositions = material_data[material_name]['compositions']
            types = material_data[material_name]['types']

            for i in range(len(elements)):
                if float(masses[i]).is_integer() or masses[i] == 0:
                    mat_object.add_element(element=elements[i],
                                           percent=compositions[i],
                                           percent_type=types[i],
                                           # enrichment=None
                                           )
                else:
                    mat_object.add_nuclide(nuclide=str(masses[i])+elements[i],
                                           percent=compositions[i],
                                           percent_type=types[i])

            MATERIALS.append(mat_object)

        model.materials = MATERIALS

        #######################################
        # Geometry

        # Determine whether root geometry is a cell or an assembly
        if root_geometry in cell_data.keys():
            # Pin Cell
            pitch_x = cell_data[root_geometry]['x-pitch']
            pitch_y = cell_data[root_geometry]['y-pitch']

            cylinders = []
            radii = cell_data[root_geometry]['radii']
            for r in range(len(radii)):
                cylinders.append(openmc.ZCylinder(x0=0, y0=0, R=radii[r], name='{} Outer Radius'.format(material_data.keys()[r])))

            # TODO: Change to total geometrical boundaries but use callback to make it nice
            left = openmc.XPlane(x0=-pitch_x / 2, name='left', boundary_type='reflective')
            right = openmc.XPlane(x0=pitch_x / 2, name='right', boundary_type='reflective')
            bottom = openmc.YPlane(y0=-pitch_y / 2, name='bottom', boundary_type='reflective')
            top = openmc.YPlane(y0=pitch_y / 2, name='top', boundary_type='reflective')

            # Instantiate Cells
            CELLS = []
            for m in range(len(MATERIALS)):
                cell = openmc.Cell(name='{}'.format(material_data.keys()[m]), fill=MATERIALS[m])
                CELLS.append(cell)

            # Use surface half-spaces to define regions
            for c in range(len(cylinders)):
                if c == 0:
                    CELLS[c].region = -cylinders[c]
                elif c == len(cylinders):
                    CELLS[c].region = +cylinders[c] & +left & -right & +bottom & -top

            # Create root universe
            model.geometry.root_universe = openmc.Universe(0, name='Root Universe')
            model.geometry.root_universe.add_cells(CELLS)

        # # Assembly
        # if root_geometry in assembly_data.keys():
        # # Instantiate ZCylinder surfaces
        # fuel_or = openmc.ZCylinder(x0=0, y0=0, R=0.39218, name='Fuel OR')
        # clad_or = openmc.ZCylinder(x0=0, y0=0, R=0.45720, name='Clad OR')
        #
        # # Create boundary planes to surround the geometry
        # pitch = 21.42
        # height = 200
        # min_x = openmc.XPlane(x0=-pitch / 2, boundary_type='reflective')
        # max_x = openmc.XPlane(x0=+pitch / 2, boundary_type='reflective')
        # min_y = openmc.YPlane(y0=-pitch / 2, boundary_type='reflective')
        # max_y = openmc.YPlane(y0=+pitch / 2, boundary_type='reflective')
        # min_z = openmc.ZPlane(z0=-height / 2, boundary_type='reflective')
        # max_z = openmc.ZPlane(z0=+height / 2, boundary_type='reflective')
        #
        # # Create a control rod guide tube universe
        # guide_tube_universe = openmc.Universe(name='Guide Tube')
        # gt_inner_cell = openmc.Cell(name='guide tube inner water', fill=hot_water,
        #                             region=-fuel_or)
        # gt_clad_cell = openmc.Cell(name='guide tube clad', fill=clad,
        #                            region=+fuel_or & -clad_or)
        # gt_outer_cell = openmc.Cell(name='guide tube outer water', fill=hot_water,
        #                             region=+clad_or)
        # guide_tube_universe.add_cells([gt_inner_cell, gt_clad_cell, gt_outer_cell])
        #
        # # Create fuel assembly Lattice
        # assembly = openmc.RectLattice(name='Fuel Assembly')
        # assembly.pitch = (pitch / 17, pitch / 17)
        # assembly.lower_left = (-pitch / 2, -pitch / 2)
        #
        # # Create array indices for guide tube locations in lattice
        # template_x = np.array([5, 8, 11, 3, 13, 2, 5, 8, 11, 14, 2, 5, 8,
        #                        11, 14, 2, 5, 8, 11, 14, 3, 13, 5, 8, 11])
        # template_y = np.array([2, 2, 2, 3, 3, 5, 5, 5, 5, 5, 8, 8, 8, 8,
        #                        8, 11, 11, 11, 11, 11, 13, 13, 14, 14, 14])
        #
        # # Create 17x17 array of universes
        # fuel_pin_universe = openmc.Universe(name='Fuel Pin')
        # fuel_cell = openmc.Cell(name='fuel', fill=fuel, region=-fuel_or)
        # clad_cell = openmc.Cell(name='clad', fill=clad, region=+fuel_or & -clad_or)
        # hot_water_cell = openmc.Cell(name='hot water', fill=hot_water, region=+clad_or)
        # fuel_pin_universe.add_cells([fuel_cell, clad_cell, hot_water_cell])
        #
        # assembly.universes = np.tile(fuel_pin_universe, (17, 17))
        # assembly.universes[template_x, template_y] = guide_tube_universe
        #
        # # Create root Cell
        # root_cell = openmc.Cell(name='root cell')
        # root_cell.fill = assembly
        # root_cell.region = +min_x & -max_x & \
        #                    +min_y & -max_y & \
        #                    +min_z & -max_z
        #
        # # Create root Universe
        # model.geometry.root_universe = openmc.Universe(name='root universe')
        # model.geometry.root_universe.add_cell(root_cell)

        #######################################
        # Mesh

        spatial_mesh = openmc.Mesh()
        spatial_mesh.type = 'regular'

        # energy_mesh = openmc.Mesh()
        for filter in score_data['filters']:
            if mesh_data[filter]['type'] == 'spatial':
                dim_x = mesh_data[filter]['x-resolution']
                dim_y = mesh_data[filter]['y-resolution']
                dim_z = mesh_data[filter]['z-resolution']
                width = mesh_data[filter]['width']
                depth = mesh_data[filter]['depth']
                height = mesh_data[filter]['height']
                spatial_mesh.dimension = [dim_x, dim_y, dim_z]
                spatial_mesh.lower_left = [-width / 2, -depth / 2, -height / 2]
                spatial_mesh.width = [width / dim_x, depth / dim_y, height / dim_z]

            # if mesh_data[filter_name]['type'] == 'energy':
                # TODO

        # Create a mesh filter
        mesh_filter = openmc.MeshFilter(spatial_mesh)

        #######################################
        # Cross-sections

        #######################################
        # Tallies/Scores

        model.tallies = openmc.Tallies()
        # mgxs_lib.add_to_tallies_file(model.tallies, merge=True)

        # Instantiate a flux tally; Other valid options: 'current', 'fission', etc
        mesh_tally = openmc.Tally(name='Mesh')
        mesh_tally.filters = [mesh_filter]
        mesh_tally.scores = score_data['scores']

        # energy_tally = openmc.Tally(name='Energy')
        # energy_tally.filters = [energy_filter]
        # energy_tally.scores = score_data['scores']

        # Add tallies to the tallies file
        model.tallies.append(mesh_tally)
        # model.tallies.append(energy_tally)

        #######################################
        # Settings TODO: Check
        model.settings.total_batches = settings_data['total-batches']
        model.settings.inactive_batches = settings_data['inactive-batches']
        model.settings.particles = settings_data['particles']
        model.settings.generations_per_batch = settings_data['gens-per-batch']
        model.settings.seed = settings_data['seed']
        model.settings.run_mode = settings_data['run-mode']
        # model.settings.energy_mode = settings_data['']
        # model.settings.cutoff = settings_data['']
        # model.settings.temperature = settings_data['']
        # model.settings.trigger_active = settings_data['']
        # model.settings.no_reduce = settings_data['']
        # model.settings.confidence_intervals = settings_data['']
        # model.settings.ptables = settings_data['']
        # model.settings.run_cmfd = settings_data['']
        # model.settings.survival_biasing = settings_data['']
        # model.settings.fission_neutrons = settings_data['']
        # model.settings.output.summary = settings_data['']
        # model.settings.output.tallies = settings_data['']
        # model.settings.output.cross_sections = settings_data['']
        # model.settings.verbosity = settings_data['']

        return html.P('Success')

#######################################################################################################################


@app.callback(
    Output('console-output', 'value'),
    [Input('run-button', 'n_clicks')], )
def run_model(click):
    if int(click) > 0:

        script_dir = os.path.dirname(__file__)
        xml_path_src = os.path.join(script_dir, '../xml-files/')
        xml_files_src = glob('{}*.xml'.format(xml_path_src))

        for file in xml_files_src:
            xml_file_name = os.path.basename(file)
            copyfile(os.path.join(xml_path_src, xml_file_name), os.path.join(script_dir, xml_file_name))

        xml_files_dst = glob('{}*.xml'.format(script_dir))
        print(xml_files_dst)

        pass_test = False
        while not pass_test:
            bool_array = []
            for file in range(len(xml_files_dst)):
                exists = os.path.exists(xml_files_dst[file])
                if exists:
                    bool_array.append(exists)

            if np.array(bool_array).all():
                pass_test = True
                print('All files exist')

            time.sleep(1)

        output = io.StringIO()
        with redirect_stdout(output):
            openmc.run()

        for file in xml_files_dst:
            os.remove(file)

        return output.getvalue()
