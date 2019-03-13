import io
import json
import os
import time
from contextlib import redirect_stdout
from glob import glob
from shutil import copyfile

import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import openmc
import openmc.mgxs
import openmc.model
from dash.dependencies import Output, State, Input

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
                'color': 'rgb(76, 1, 3)'
            }), html.Br(),

    #############################################################################
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
            dcc.Textarea(id='geometry-xml',
                         placeholder='Write XML contents here and Load to File or leave blank and Load from File',
                         style=dict(width='100%', height='250px')),
            html.Br(),
            html.Button('Load Geometry XML File', n_clicks=0, id='load-geometry'),
            html.Button('Write Geometry XML File', n_clicks=0, id='write-geometry'),
            html.P(id='geometry-placeholder'),  # Used as dummy for mandatory Output in decorator

            html.Label('Plots XML File Contents'),
            html.Br(),
            dcc.Textarea(id='plots-xml',
                         placeholder='Write XML contents here and Load to File or leave blank and Load from File',
                         style=dict(width='100%', height='250px')),
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
            dcc.Textarea(id='materials-xml',
                         placeholder='Write XML contents here and Load to File or leave blank and Load from File',
                         style=dict(width='100%', height='250px')),
            html.Br(),
            html.Button('Load Material XML File', n_clicks=0, id='load-materials'),
            html.Button('Write Material XML File', n_clicks=0, id='write-materials'),
            html.P(id='material-placeholder'),  # Used as dummy for mandatory Output in decorator
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
            dcc.Textarea(id='tallies-xml',
                         placeholder='Write XML contents here and Load to File or leave blank and Load from File',
                         style=dict(width='100%', height='250px')),
            html.Br(),
            html.Button('Load Tallies XML File', n_clicks=0, id='load-tallies'),
            html.Button('Write Tallies XML File', n_clicks=0, id='write-tallies'),
            html.P(id='tallies-placeholder'),  # Used as dummy for mandatory Output in decorator

            html.Label('Settings XML File Contents'),
            html.Br(),
            dcc.Textarea(id='settings-xml',
                         placeholder='Write XML contents here and Load to File or leave blank and Load from File',
                         style=dict(width='100%', height='250px')),
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
    html.Br(),
    html.Div(id='memory-display'),
    html.Button('Run Simulation', id='run-button', n_clicks=0),
    html.Br(),
    dcc.Textarea(id='console-output', placeholder='Console Output will appear here...',
                 readOnly=True, style=dict(width='100%', height='250px')),
])


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

    [State('material-stores', 'data'),

     State('cell-stores', 'data'),
     State('assembly-stores', 'data'),
     State('geometry-stores', 'data'),

     State('mesh-score-stores', 'data'),
     State('xsection-stores', 'data'),

     State('settings-stores', 'data')]
)
def build_model(click, material_data, cell_data, assembly_data, geometry_data, score_data, xsection_data,
                settings_data):
    if click:
        model = openmc.model.Model()

        print(json.dumps(material_data, indent=2))
        print(json.dumps(cell_data, indent=2))
        print(json.dumps(assembly_data, indent=2))
        print(json.dumps(geometry_data, indent=2))
        print(json.dumps(score_data, indent=2))
        print(json.dumps(settings_data, indent=2))

        #######################################
        # Materials DONE

        MATERIALS = openmc.Materials([])
        MATERIALS_DICT = {}
        for material_name in material_data.keys():
            mat_object = openmc.Material(name=material_name)

            if 'temperature' in list(material_data[material_name].keys()) and material_data[material_name][
                'temperature'] != 0:
                mat_object.temperature = material_data[material_name]['temperature']
            mat_object.set_density('g/cm3', material_data[material_name]['density'])
            mat_object.depletable = False

            elements = material_data[material_name]['elements']
            masses = material_data[material_name]['masses']
            compositions = material_data[material_name]['compositions']
            types = material_data[material_name]['types']

            for i in range(len(elements)):
                if not float(masses[i]).is_integer() or masses[i] == 0:
                    mat_object.add_element(element=elements[i],
                                           percent=compositions[i],
                                           percent_type=types[i],
                                           # enrichment=None
                                           )
                else:
                    mat_object.add_nuclide(nuclide=elements[i] + str(masses[i]),
                                           percent=compositions[i],
                                           percent_type=types[i])

            MATERIALS.append(mat_object)
            MATERIALS_DICT.update({'{}'.format(material_name): mat_object})

        model.materials = MATERIALS
        script_dir = os.path.dirname(__file__)
        xsections_file = os.path.join(script_dir, '../nndc_hdf5/cross_sections.xml')
        model.materials.cross_sections = xsections_file

        #######################################
        # Geometry

        # Determine whether root geometry is a cell or an assembly
        root_geometry = geometry_data['root-geometry']
        if root_geometry in cell_data.keys():
            # Pin Cell
            pitch_x = cell_data[root_geometry]['x-pitch']
            pitch_y = cell_data[root_geometry]['y-pitch']
            height_z = cell_data[root_geometry]['height']

            cylinders = []
            cell_radii = cell_data[root_geometry]['radii']
            for r in range(len(cell_radii)):
                cylinders.append(openmc.ZCylinder(x0=0, y0=0, R=cell_radii[r],
                                                  name='{} Outer Radius'.format(list(material_data.keys())[r])))

            x_neg = openmc.XPlane(x0=-pitch_x / 2, name='x-neg', boundary_type='reflective')
            x_pos = openmc.XPlane(x0=pitch_x / 2, name='x-pos', boundary_type='reflective')
            y_neg = openmc.YPlane(y0=-pitch_y / 2, name='y-neg', boundary_type='reflective')
            y_pos = openmc.YPlane(y0=pitch_y / 2, name='y-pos', boundary_type='reflective')
            bottom = openmc.ZPlane(z0=-height_z / 2, name='z-neg', boundary_type='reflective')
            top = openmc.ZPlane(z0=height_z / 2, name='z-pos', boundary_type='reflective')

            # Instantiate Cells
            CELLS = []
            cell_materials = cell_data[root_geometry]['materials']
            for m in range(len(cell_materials)):
                cell = openmc.Cell(name='{}'.format(cell_materials[m]), fill=MATERIALS_DICT[cell_materials[m]])
                CELLS.append(cell)

            # Use surface half-spaces to define regions
            for c in range(len(cylinders)):
                if c == 0:
                    CELLS[c].region = -cylinders[c]
                elif c == len(cylinders) - 1:
                    CELLS[c].region = +cylinders[c] & +x_neg & -x_pos & +y_neg & -y_pos & +bottom & -top
                else:
                    CELLS[c].region = +cylinders[c] & -cylinders[c + 1]

            # Create root universe
            model.geometry.root_universe = openmc.Universe(0, name='Root Universe')
            model.geometry.root_universe.add_cells(CELLS)

        # Assembly
        if root_geometry in assembly_data.keys():
            # Main Cell
            dim_x = cell_data[assembly_data[root_geometry]['main-cell']]['x-pitch'] * \
                    assembly_data[root_geometry]['assembly-metrics']['assembly-num-x']
            dim_y = cell_data[assembly_data[root_geometry]['main-cell']]['y-pitch'] * \
                    assembly_data[root_geometry]['assembly-metrics']['assembly-num-y']
            dim_z = cell_data[assembly_data[root_geometry]['main-cell']]['height']

            # Create boundary planes to surround the geometry
            min_x = openmc.XPlane(x0=-dim_x / 2, boundary_type='reflective')
            max_x = openmc.XPlane(x0=+dim_x / 2, boundary_type='reflective')
            min_y = openmc.YPlane(y0=-dim_y / 2, boundary_type='reflective')
            max_y = openmc.YPlane(y0=+dim_y / 2, boundary_type='reflective')
            min_z = openmc.ZPlane(z0=-dim_z / 2, boundary_type='reflective')
            max_z = openmc.ZPlane(z0=+dim_z / 2, boundary_type='reflective')

            main_cylinders = []
            main_cell_radii = cell_data[assembly_data[root_geometry]['main-cell']]['radii']
            for r in range(len(main_cell_radii)):
                main_cylinders.append(openmc.ZCylinder(x0=0, y0=0, R=main_cell_radii[r],
                                                       name='{} Outer Radius'.format(list(material_data.keys())[r])))

            MAIN_CELLS = []
            main_cell_materials = cell_data[assembly_data[root_geometry]['main-cell']]['materials']
            for m in range(len(main_cell_materials)):
                cell = openmc.Cell(name='{}'.format(main_cell_materials[m]), fill=MATERIALS_DICT[main_cell_materials[m]])
                MAIN_CELLS.append(cell)

            for c in range(len(main_cylinders)):
                if c == 0:
                    MAIN_CELLS[c].region = -main_cylinders[c]
                elif c == len(main_cylinders) - 1:
                    MAIN_CELLS[c].region = +main_cylinders[c] & +min_x & -max_x & +min_y & -max_y & +min_z & -max_z
                else:
                    MAIN_CELLS[c].region = +main_cylinders[c] & -main_cylinders[c + 1]

            main_universe = openmc.Universe(name='Main Pin Cell')
            main_universe.add_cells(MAIN_CELLS)

            # # Create fuel assembly Lattice
            assembly = openmc.RectLattice(name='{}'.format(root_geometry))
            assembly.pitch = (
                cell_data[assembly_data[root_geometry]['main-cell']]['x-pitch'],
                cell_data[assembly_data[root_geometry]['main-cell']]['y-pitch'])
            assembly.lower_left = (-dim_x / 2, -dim_y / 2)
            # noinspection PyTypeChecker
            assembly.universes = np.tile(main_universe,
                                         (assembly_data[root_geometry]['assembly-metrics']['assembly-num-x'],
                                          assembly_data[root_geometry]['assembly-metrics']['assembly-num-y']))

            for injected_cell in assembly_data[root_geometry]['injected-cells'].keys():
                injection_cylinders = []
                injection_cell_radii = cell_data[injected_cell]['radii']
                for r in range(len(injection_cell_radii)):
                    injection_cylinders.append(openmc.ZCylinder(x0=0, y0=0, R=injection_cell_radii[r],
                                                                name='{} Outer Radius'.format(
                                                                    list(material_data.keys())[r])))

                INJECTION_CELLS = []
                injected_cell_materials = cell_data[injected_cell]['materials']
                for m in range(len(injected_cell_materials)):
                    cell = openmc.Cell(name='{}'.format(injected_cell_materials[m]), fill=MATERIALS_DICT[injected_cell_materials[m]])
                    INJECTION_CELLS.append(cell)

                for c in range(len(injection_cylinders)):
                    if c == 0:
                        INJECTION_CELLS[c].region = -injection_cylinders[c]
                    elif c == len(injection_cylinders) - 1:
                        INJECTION_CELLS[c].region = +injection_cylinders[
                            c] & +min_x & -max_x & +min_y & -max_y & +min_z & -max_z
                    else:
                        INJECTION_CELLS[c].region = +injection_cylinders[c] & -injection_cylinders[c + 1]

                injected_universe = openmc.Universe(name='{} Cell'.format(injected_cell))
                injected_universe.add_cells(INJECTION_CELLS)

                # Create array indices for guide tube locations in lattice
                indices_x = np.array(assembly_data[root_geometry]['injected-cells'][injected_cell]['indices'][:, 0])
                indices_y = np.array(assembly_data[root_geometry]['injected-cells'][injected_cell]['indices'][:, 1])

                assembly.universes[indices_x, indices_y] = injected_universe

            # Create Assembly Root Cell
            root_cell = openmc.Cell(name='Root Cell')
            root_cell.fill = assembly
            root_cell.region = +min_x & -max_x & \
                               +min_y & -max_y & \
                               +min_z & -max_z

            # # Create root Universe
            model.geometry.root_universe = openmc.Universe(name='Root Universe')
            model.geometry.root_universe.add_cell(root_cell)

        plot = openmc.Plot().from_geometry(model.geometry)
        plot.filename = 'ModelGeometry'
        plot.pixels = (3000, 3000)
        plot.basis = 'xy'
        # plot.color_by = 'material'
        model.plots.append(plot)
        openmc.plot_geometry(output=True)

        #######################################
        # Mesh
        spatial_mesh = openmc.Mesh()
        spatial_mesh.type = 'regular'

        # energy_mesh = openmc.Mesh()
        for filter in score_data['filters']:
            if filter['type'] == 'spatial':
                res_x = filter['x-resolution']
                res_y = filter['y-resolution']
                res_z = filter['z-resolution']
                width = filter['width']
                depth = filter['depth']
                height = filter['height']
                spatial_mesh.dimension = [res_x, res_y, res_z]
                spatial_mesh.lower_left = [-width / 2, -depth / 2, -height / 2]
                spatial_mesh.width = [width / res_x, depth / res_y, height / res_z]

            # if mesh_data[filter_name]['type'] == 'energy':
            # TODO

        # Create a mesh filter
        mesh_filter = openmc.MeshFilter(spatial_mesh)

        #######################################
        # Cross-sections

        if xsection_data:
            energy_groups = openmc.mgxs.EnergyGroups()
            energy_start = xsection_data['energy-start']
            energy_end = xsection_data['energy-end']
            if xsection_data['energy-spacing'] == 'log':
                energy_bounds = np.logspace(np.log10(energy_start), np.log10(energy_end),
                                            xsection_data['energy-groups'] + 1)
                energy_groups.group_edges = energy_bounds
            elif xsection_data['energy-spacing'] == 'lin':
                energy_bounds = np.linspace(energy_start, energy_end, xsection_data['energy-groups'] + 1)
                energy_groups.group_edges = energy_bounds

            # Initialize an 20-energy-group and 6-delayed-group MGXS Library
            mgxs_lib = openmc.mgxs.Library(model.geometry)
            mgxs_lib.energy_groups = energy_groups
            mgxs_lib.num_delayed_groups = xsection_data['delayed-groups']
            #
            # # Specify multi-group cross section types to compute
            mgxs_lib.mgxs_types = xsection_data['xsection-types']

            # # Specify a "mesh" domain type for the cross section tally filters
            mgxs_lib.domain_type = 'mesh'
            # # Specify the mesh domain over which to compute multi-group cross sections
            mgxs_lib.domains = [spatial_mesh]

            # Construct all tallies needed for the multi-group cross section library
            mgxs_lib.build_library()

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
        model.settings.batches = settings_data['total-batches']
        model.settings.inactive = settings_data['inactive-batches']
        model.settings.particles = settings_data['particles']
        model.settings.generations_per_batch = settings_data['gens-per-batch']
        model.settings.seed = settings_data['seed']
        # Source is iterable
        model.settings.source = openmc.Source(space=openmc.stats.Box(
            [-width / 2, -depth / 2, -height / 2], [width / 2, depth / 2, height / 2]))
        # model.settings.energy_mode = settings_data['energy-mode']
        model.settings.run_mode = settings_data['run-mode']

        # model.settings.cutoff = settings_data['']
        # model.settings.temperature = settings_data['']
        # model.settings.trigger_active = settings_data['']
        # model.settings.no_reduce = settings_data['']
        model.settings.confidence_intervals = settings_data['confidence-intervals']
        model.settings.ptables = settings_data['ptables']
        model.settings.run_cmfd = settings_data['run-cmfd']
        model.settings.survival_biasing = settings_data['survival-biasing']
        model.settings.fission_neutrons = settings_data['fission-neutrons']
        model.settings.output = {'summary': settings_data['output-summary'], 'tallies': settings_data['output-tallies']}
        model.settings.verbosity = settings_data['verbosity']

        # model.settings.state_point = dict
        # model.settings.source_point = dict
        # model.settings.threads = int
        # model.settings.trace = tuple or list
        # model.settings.track = tuple or list

        print("Exporting to xml...")
        model.export_to_xml()
        return html.P('Success')


#######################################################################################################################


@app.callback(
    Output('console-output', 'value'),
    [Input('run-button', 'n_clicks')], )
def run_model(click):
    if click:

        script_dir = os.path.dirname(__file__)
        xml_path_src = os.path.join(script_dir, './parameters/')  # TODO: Change to './xml-files/' eventually
        xml_files_src = glob('{}*.xml'.format(xml_path_src))

        for file in xml_files_src:
            xml_file_name = os.path.basename(file)
            copyfile(file, os.path.join(script_dir, xml_file_name))
            os.remove(file)

        xml_files_dst = glob('*.xml')
        all_files_exist = False
        while not all_files_exist:
            bool_array = []
            for file in range(len(xml_files_dst)):
                exists = os.path.exists(xml_files_dst[file])
                if exists:
                    bool_array.append(exists)

            if np.array(bool_array).all() and len(xml_files_dst) > 0:
                all_files_exist = True
                print('All files exist')

            time.sleep(1)

        output = io.StringIO()
        with redirect_stdout(output):
            openmc.run()

        for file in xml_files_dst:
            os.remove(file)

        return output.getvalue()
