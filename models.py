import numpy as np
import openmc
import openmc.mgxs
import openmc.model
import pandas as pd
import plotly
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode

init_notebook_mode(connected=True)


def slab_mg(reps=None, as_macro=True):
    """Create a one-group, 1D slab model.

    Parameters
    ----------
    reps : list, optional
        List of angular representations. Each item corresponds to materials and
        dictates the angular representation of the multi-group cross
        sections---isotropic ('iso') or angle-dependent ('ang'), and if Legendre
        scattering or tabular scattering ('mu') is used. Thus, items can be
        'ang', 'ang_mu', 'iso', or 'iso_mu'.

    as_macro : bool, optional
        Whether :class:`openmc.Macroscopic` is used

    Returns
    -------
    model : openmc.model.Model
        One-group, 1D slab model

    """
    model = openmc.model.Model()

    # Define materials needed for 1D/1G slab problem
    mat_names = ['uo2', 'clad', 'lwtr']
    mgxs_reps = ['ang', 'ang_mu', 'iso', 'iso_mu']

    if reps is None:
        reps = mgxs_reps

    xs = []
    i = 0
    for mat in mat_names:
        for rep in reps:
            i += 1
            name = mat + '_' + rep
            xs.append(name)
            if as_macro:
                m = openmc.Material(name=str(i))
                m.set_density('macro', 1.)
                m.add_macroscopic(name)
            else:
                m = openmc.Material(name=str(i))
                m.set_density('atom/b-cm', 1.)
                m.add_nuclide(name, 1.0, 'ao')
            model.materials.append(m)

    # Define the materials file
    model.xs_data = xs
    model.materials.cross_sections = "../1d_mgxs.h5"

    # Define surfaces.
    # Assembly/Problem Boundary
    left = openmc.XPlane(x0=0.0, boundary_type='reflective')
    right = openmc.XPlane(x0=10.0, boundary_type='reflective')
    bottom = openmc.YPlane(y0=0.0, boundary_type='reflective')
    top = openmc.YPlane(y0=10.0, boundary_type='reflective')

    # for each material add a plane
    planes = [openmc.ZPlane(z0=0.0, boundary_type='reflective')]
    dz = round(5. / float(len(model.materials)), 4)
    for i in range(len(model.materials) - 1):
        planes.append(openmc.ZPlane(z0=dz * float(i + 1)))
    planes.append(openmc.ZPlane(z0=5.0, boundary_type='reflective'))

    # Define cells for each material
    model.geometry.root_universe = openmc.Universe(name='root universe')
    xy = +left & -right & +bottom & -top
    for i, mat in enumerate(model.materials):
        c = openmc.Cell(fill=mat, region=xy & +planes[i] & -planes[i + 1])
        model.geometry.root_universe.add_cell(c)

    model.settings.batches = 20
    model.settings.inactive = 5
    model.settings.particles = 200
    model.settings.source = openmc.Source(space=openmc.stats.Box(
        [0.0, 0.0, 0.0], [10.0, 10.0, 5.]))
    model.settings.energy_mode = "multi-group"

    plot = openmc.Plot()
    plot.filename = 'mat'
    plot.origin = (5.0, 5.0, 2.5)
    plot.width = (2.5, 2.5)
    plot.basis = 'xz'
    plot.pixels = (3000, 3000)
    plot.color_by = 'material'
    model.plots.append(plot)

    return model


def pwr_pin_cell():
    """Create a PWR pin-cell model.

    This model is a single fuel pin with 2.4 w/o enriched UO2 corresponding to a
    beginning-of-cycle condition and borated water. The specifications are from
    the `BEAVRS <http://crpg.mit.edu/research/beavrs>`_ benchmark. Note that the
    number of particles/batches is initially set very low for testing purposes.

    Returns
    -------
    model : openmc.model.Model
        A PWR pin-cell model

    """
    model = openmc.model.Model()

    # Define materials.
    fuel = openmc.Material(name='UO2 (2.4%)')
    fuel.set_density('g/cm3', 10.29769)
    fuel.add_nuclide("U234", 4.4843e-6)
    fuel.add_nuclide("U235", 5.5815e-4)
    fuel.add_nuclide("U238", 2.2408e-2)
    fuel.add_nuclide("O16", 4.5829e-2)

    clad = openmc.Material(name='Zircaloy')
    clad.set_density('g/cm3', 6.55)
    clad.add_nuclide("Zr90", 2.1827e-2)
    clad.add_nuclide("Zr91", 4.7600e-3)
    clad.add_nuclide("Zr92", 7.2758e-3)
    clad.add_nuclide("Zr94", 7.3734e-3)
    clad.add_nuclide("Zr96", 1.1879e-3)

    hot_water = openmc.Material(name='Hot borated water')
    hot_water.set_density('g/cm3', 0.740582)
    hot_water.add_nuclide("H1", 4.9457e-2)
    hot_water.add_nuclide("O16", 2.4672e-2)
    hot_water.add_nuclide("B10", 8.0042e-6)
    hot_water.add_nuclide("B11", 3.2218e-5)
    hot_water.add_s_alpha_beta('c_H_in_H2O')

    # Define the materials file.
    model.materials = (fuel, clad, hot_water)

    # Instantiate ZCylinder surfaces
    pitch = 1.26
    fuel_or = openmc.ZCylinder(x0=0, y0=0, R=0.39218, name='Fuel OR')
    clad_or = openmc.ZCylinder(x0=0, y0=0, R=0.45720, name='Clad OR')
    left = openmc.XPlane(x0=-pitch / 2, name='left', boundary_type='reflective')
    right = openmc.XPlane(x0=pitch / 2, name='right', boundary_type='reflective')
    bottom = openmc.YPlane(y0=-pitch / 2, name='bottom', boundary_type='reflective')
    top = openmc.YPlane(y0=pitch / 2, name='top', boundary_type='reflective')

    # Instantiate Cells
    fuel_pin = openmc.Cell(name='Fuel', fill=fuel)
    cladding = openmc.Cell(name='Cladding', fill=clad)
    water = openmc.Cell(name='Water', fill=hot_water)

    # Use surface half-spaces to define regions
    fuel_pin.region = -fuel_or
    cladding.region = +fuel_or & -clad_or
    water.region = +clad_or & +left & -right & +bottom & -top

    # Create root universe
    model.geometry.root_universe = openmc.Universe(0, name='root universe')
    model.geometry.root_universe.add_cells([fuel_pin, cladding, water])

    model.settings.batches = 10
    model.settings.inactive = 5
    model.settings.particles = 100
    model.settings.source = openmc.Source(space=openmc.stats.Box(
        [-pitch / 2, -pitch / 2, -1], [pitch / 2, pitch / 2, 1], only_fissionable=True))

    plot = openmc.Plot.from_geometry(model.geometry)
    plot.pixels = (300, 300)
    plot.color_by = 'material'
    model.plots.append(plot)

    return model


def pwr_assembly():
    """Create a PWR assembly model.

    This model is a reflected 17x17 fuel assembly from the the `BEAVRS
    <http://crpg.mit.edu/research/beavrs>`_ benchmark. The fuel is 2.4 w/o
    enriched UO2 corresponding to a beginning-of-cycle condition. Note that the
    number of particles/batches is initially set very low for testing purposes.

    Returns
    -------
    model : openmc.model.Model
        A PWR assembly model

    """

    model = openmc.model.Model()

    ############################################################################################################
    # MATERIALS

    # Define materials.
    fuel = openmc.Material(name='Fuel')
    fuel.set_density('g/cm3', 10.29769)
    fuel.add_nuclide("U234", 4.4843e-6)
    fuel.add_nuclide("U235", 5.5815e-4)
    fuel.add_nuclide("U238", 2.2408e-2)
    fuel.add_nuclide("O16", 4.5829e-2)

    clad = openmc.Material(name='Cladding')
    clad.set_density('g/cm3', 6.55)
    clad.add_nuclide("Zr90", 2.1827e-2)
    clad.add_nuclide("Zr91", 4.7600e-3)
    clad.add_nuclide("Zr92", 7.2758e-3)
    clad.add_nuclide("Zr94", 7.3734e-3)
    clad.add_nuclide("Zr96", 1.1879e-3)

    hot_water = openmc.Material(name='Hot borated water')
    hot_water.set_density('g/cm3', 0.740582)
    hot_water.add_nuclide("H1", 4.9457e-2)
    hot_water.add_nuclide("O16", 2.4672e-2)
    hot_water.add_nuclide("B10", 8.0042e-6)
    hot_water.add_nuclide("B11", 3.2218e-5)
    hot_water.add_s_alpha_beta('c_H_in_H2O')

    # Define the materials file.
    model.materials = (fuel, clad, hot_water)

    ############################################################################################################
    # GEOMETRY

    # Instantiate ZCylinder surfaces
    fuel_or = openmc.ZCylinder(x0=0, y0=0, R=0.39218, name='Fuel OR')
    clad_or = openmc.ZCylinder(x0=0, y0=0, R=0.45720, name='Clad OR')

    # Create boundary planes to surround the geometry
    pitch = 21.42
    height = 200
    min_x = openmc.XPlane(x0=-pitch / 2, boundary_type='reflective')
    max_x = openmc.XPlane(x0=+pitch / 2, boundary_type='reflective')
    min_y = openmc.YPlane(y0=-pitch / 2, boundary_type='reflective')
    max_y = openmc.YPlane(y0=+pitch / 2, boundary_type='reflective')
    min_z = openmc.ZPlane(z0=-height / 2, boundary_type='reflective')
    max_z = openmc.ZPlane(z0=+height / 2, boundary_type='reflective')

    # Create a control rod guide tube universe
    guide_tube_universe = openmc.Universe(name='Guide Tube')
    gt_inner_cell = openmc.Cell(name='guide tube inner water', fill=hot_water,
                                region=-fuel_or)
    gt_clad_cell = openmc.Cell(name='guide tube clad', fill=clad,
                               region=+fuel_or & -clad_or)
    gt_outer_cell = openmc.Cell(name='guide tube outer water', fill=hot_water,
                                region=+clad_or)
    guide_tube_universe.add_cells([gt_inner_cell, gt_clad_cell, gt_outer_cell])

    # Create fuel assembly Lattice
    assembly = openmc.RectLattice(name='Fuel Assembly')
    assembly.pitch = (pitch / 17, pitch / 17)
    assembly.lower_left = (-pitch / 2, -pitch / 2)

    # Create array indices for guide tube locations in lattice
    template_x = np.array([5, 8, 11, 3, 13, 2, 5, 8, 11, 14, 2, 5, 8,
                           11, 14, 2, 5, 8, 11, 14, 3, 13, 5, 8, 11])
    template_y = np.array([2, 2, 2, 3, 3, 5, 5, 5, 5, 5, 8, 8, 8, 8,
                           8, 11, 11, 11, 11, 11, 13, 13, 14, 14, 14])

    # Create 17x17 array of universes
    fuel_pin_universe = openmc.Universe(name='Fuel Pin')
    fuel_cell = openmc.Cell(name='fuel', fill=fuel, region=-fuel_or)
    clad_cell = openmc.Cell(name='clad', fill=clad, region=+fuel_or & -clad_or)
    hot_water_cell = openmc.Cell(name='hot water', fill=hot_water, region=+clad_or)
    fuel_pin_universe.add_cells([fuel_cell, clad_cell, hot_water_cell])

    assembly.universes = np.tile(fuel_pin_universe, (17, 17))
    assembly.universes[template_x, template_y] = guide_tube_universe

    # Create root Cell
    root_cell = openmc.Cell(name='root cell')
    root_cell.fill = assembly
    root_cell.region = +min_x & -max_x & \
                       +min_y & -max_y & \
                       +min_z & -max_z

    # Create root Universe
    model.geometry.root_universe = openmc.Universe(name='root universe')
    model.geometry.root_universe.add_cell(root_cell)

    ############################################################################################################
    # MESH

    mesh = openmc.Mesh(mesh_id=1)
    mesh.type = 'regular'
    dim_x, dim_y, dim_z = [100, 100, 10]
    mesh.dimension = [dim_x, dim_y, dim_z]
    mesh.lower_left = [*assembly.lower_left, -height / 2]
    mesh.width = [*assembly.pitch, height / dim_z]

    # Create a mesh filter
    mesh_filter = openmc.MeshFilter(mesh)

    ############################################################################################################
    # CROSS-SECTION LIBRARY

    energy_groups = openmc.mgxs.EnergyGroups()
    energy_groups.group_edges = np.logspace(-3, 7.3, 21)

    # Instantiate a 1-group EnergyGroups object
    one_group = openmc.mgxs.EnergyGroups()
    one_group.group_edges = np.array([energy_groups.group_edges[0], energy_groups.group_edges[-1]])

    # Initialize an 20-energy-group and 6-delayed-group MGXS Library
    mgxs_lib = openmc.mgxs.Library(model.geometry)
    mgxs_lib.energy_groups = one_group
    mgxs_lib.num_delayed_groups = 6

    # Specify multi-group cross section types to compute
    mgxs_lib.mgxs_types = ['total', 'transport', 'nu-scatter matrix', 'kappa-fission', 'inverse-velocity', 'chi-prompt',
                           'prompt-nu-fission', 'chi-delayed', 'delayed-nu-fission', 'beta']
    # Specify a "mesh" domain type for the cross section tally filters
    mgxs_lib.domain_type = 'mesh'
    # Specify the mesh domain over which to compute multi-group cross sections
    mgxs_lib.domains = [mesh]

    # Construct all tallies needed for the multi-group cross section library
    mgxs_lib.build_library()

    ############################################################################################################
    # TALLIES

    # Create a "tallies.xml" file for the MGXS Library
    model.tallies = openmc.Tallies()
    mgxs_lib.add_to_tallies_file(model.tallies, merge=True)

    # Instantiate a flux tally; Other valid options: 'current', 'fission', etc
    flux_tally = openmc.Tally(name='Flux')
    flux_tally.filters = [mesh_filter]
    flux_tally.scores = ['flux']

    # Add tallies to the tallies file
    model.tallies.append(flux_tally)

    ############################################################################################################
    # SETTINGS

    model.settings.batches = 10
    model.settings.inactive = 5
    model.settings.particles = 100
    model.settings.source = openmc.Source(space=openmc.stats.Box(
        [-pitch / 2, -pitch / 2, -height / 2], [pitch / 2, pitch / 2, height / 2], only_fissionable=True))

    ############################################################################################################
    # PLOT

    plot = openmc.Plot()
    plot.origin = (0.0, 0.0, 0)
    plot.width = (21.42, 21.42)
    plot.pixels = (300, 300)
    plot.color_by = 'material'
    model.plots.append(plot)

    openmc.plot_geometry(output=False)

    return model


def pwr_core():
    """Create a PWR full-core model.

    This model is the OECD/NEA Monte Carlo Performance benchmark which is a
    grossly simplified pressurized water reactor (PWR) with 241 fuel
    assemblies. Note that the number of particles/batches is initially set very
    low for testing purposes.

    Returns
    -------
    model : openmc.model.Model
        Full-core PWR model

    """
    model = openmc.model.Model()

    ############################################################################################################
    # MATERIALS

    # Define materials.

    # 1 Fuel
    fuel = openmc.Material(1, name='UOX fuel')
    fuel.depletable = True
    fuel.set_density('g/cm3', 10.062)
    fuel.add_nuclide("U234", 4.9476e-6)
    fuel.add_nuclide("U235", 4.8218e-4)
    fuel.add_nuclide("U238", 2.1504e-2)
    fuel.add_nuclide("Xe135", 1.0801e-8)
    fuel.add_nuclide("O16", 4.5737e-2)

    clad = openmc.Material(2, name='Zircaloy')
    clad.set_density('g/cm3', 5.77)
    clad.add_nuclide("Zr90", 0.5145)
    clad.add_nuclide("Zr91", 0.1122)
    clad.add_nuclide("Zr92", 0.1715)
    clad.add_nuclide("Zr94", 0.1738)
    clad.add_nuclide("Zr96", 0.0280)

    cold_water = openmc.Material(3, name='Cold borated water')
    cold_water.set_density('atom/b-cm', 0.07416)
    cold_water.add_nuclide("H1", 2.0)
    cold_water.add_nuclide("O16", 1.0)
    cold_water.add_nuclide("B10", 6.490e-4)
    cold_water.add_nuclide("B11", 2.689e-3)
    cold_water.add_s_alpha_beta('c_H_in_H2O')

    hot_water = openmc.Material(4, name='Hot borated water')
    hot_water.set_density('atom/b-cm', 0.06614)
    hot_water.add_nuclide("H1", 2.0)
    hot_water.add_nuclide("O16", 1.0)
    hot_water.add_nuclide("B10", 6.490e-4)
    hot_water.add_nuclide("B11", 2.689e-3)
    hot_water.add_s_alpha_beta('c_H_in_H2O')

    rpv_steel = openmc.Material(5, name='Reactor pressure vessel steel')
    rpv_steel.set_density('g/cm3', 7.9)
    rpv_steel.add_nuclide("Fe54", 0.05437098, 'wo')
    rpv_steel.add_nuclide("Fe56", 0.88500663, 'wo')
    rpv_steel.add_nuclide("Fe57", 0.0208008, 'wo')
    rpv_steel.add_nuclide("Fe58", 0.00282159, 'wo')
    rpv_steel.add_nuclide("Ni58", 0.0067198, 'wo')
    rpv_steel.add_nuclide("Ni60", 0.0026776, 'wo')
    rpv_steel.add_nuclide("Mn55", 0.01, 'wo')
    rpv_steel.add_nuclide("Cr52", 0.002092475, 'wo')
    rpv_steel.add_nuclide("C0", 0.0025, 'wo')
    rpv_steel.add_nuclide("Cu63", 0.0013696, 'wo')

    lower_rad_ref = openmc.Material(6, name='Lower radial reflector')
    lower_rad_ref.set_density('g/cm3', 4.32)
    lower_rad_ref.add_nuclide("H1", 0.0095661, 'wo')
    lower_rad_ref.add_nuclide("O16", 0.0759107, 'wo')
    lower_rad_ref.add_nuclide("B10", 3.08409e-5, 'wo')
    lower_rad_ref.add_nuclide("B11", 1.40499e-4, 'wo')
    lower_rad_ref.add_nuclide("Fe54", 0.035620772088, 'wo')
    lower_rad_ref.add_nuclide("Fe56", 0.579805982228, 'wo')
    lower_rad_ref.add_nuclide("Fe57", 0.01362750048, 'wo')
    lower_rad_ref.add_nuclide("Fe58", 0.001848545204, 'wo')
    lower_rad_ref.add_nuclide("Ni58", 0.055298376566, 'wo')
    lower_rad_ref.add_nuclide("Mn55", 0.0182870, 'wo')
    lower_rad_ref.add_nuclide("Cr52", 0.145407678031, 'wo')
    lower_rad_ref.add_s_alpha_beta('c_H_in_H2O')

    upper_rad_ref = openmc.Material(7, name='Upper radial reflector / Top plate region')
    upper_rad_ref.set_density('g/cm3', 4.28)
    upper_rad_ref.add_nuclide("H1", 0.0086117, 'wo')
    upper_rad_ref.add_nuclide("O16", 0.0683369, 'wo')
    upper_rad_ref.add_nuclide("B10", 2.77638e-5, 'wo')
    upper_rad_ref.add_nuclide("B11", 1.26481e-4, 'wo')
    upper_rad_ref.add_nuclide("Fe54", 0.035953677186, 'wo')
    upper_rad_ref.add_nuclide("Fe56", 0.585224740891, 'wo')
    upper_rad_ref.add_nuclide("Fe57", 0.01375486056, 'wo')
    upper_rad_ref.add_nuclide("Fe58", 0.001865821363, 'wo')
    upper_rad_ref.add_nuclide("Ni58", 0.055815129186, 'wo')
    upper_rad_ref.add_nuclide("Mn55", 0.0184579, 'wo')
    upper_rad_ref.add_nuclide("Cr52", 0.146766614995, 'wo')
    upper_rad_ref.add_s_alpha_beta('c_H_in_H2O')

    bot_plate = openmc.Material(8, name='Bottom plate region')
    bot_plate.set_density('g/cm3', 7.184)
    bot_plate.add_nuclide("H1", 0.0011505, 'wo')
    bot_plate.add_nuclide("O16", 0.0091296, 'wo')
    bot_plate.add_nuclide("B10", 3.70915e-6, 'wo')
    bot_plate.add_nuclide("B11", 1.68974e-5, 'wo')
    bot_plate.add_nuclide("Fe54", 0.03855611055, 'wo')
    bot_plate.add_nuclide("Fe56", 0.627585036425, 'wo')
    bot_plate.add_nuclide("Fe57", 0.014750478, 'wo')
    bot_plate.add_nuclide("Fe58", 0.002000875025, 'wo')
    bot_plate.add_nuclide("Ni58", 0.059855207342, 'wo')
    bot_plate.add_nuclide("Mn55", 0.0197940, 'wo')
    bot_plate.add_nuclide("Cr52", 0.157390026871, 'wo')
    bot_plate.add_s_alpha_beta('c_H_in_H2O')

    bot_nozzle = openmc.Material(9, name='Bottom nozzle region')
    bot_nozzle.set_density('g/cm3', 2.53)
    bot_nozzle.add_nuclide("H1", 0.0245014, 'wo')
    bot_nozzle.add_nuclide("O16", 0.1944274, 'wo')
    bot_nozzle.add_nuclide("B10", 7.89917e-5, 'wo')
    bot_nozzle.add_nuclide("B11", 3.59854e-4, 'wo')
    bot_nozzle.add_nuclide("Fe54", 0.030411411144, 'wo')
    bot_nozzle.add_nuclide("Fe56", 0.495012237964, 'wo')
    bot_nozzle.add_nuclide("Fe57", 0.01163454624, 'wo')
    bot_nozzle.add_nuclide("Fe58", 0.001578204652, 'wo')
    bot_nozzle.add_nuclide("Ni58", 0.047211231662, 'wo')
    bot_nozzle.add_nuclide("Mn55", 0.0156126, 'wo')
    bot_nozzle.add_nuclide("Cr52", 0.124142524198, 'wo')
    bot_nozzle.add_s_alpha_beta('c_H_in_H2O')

    top_nozzle = openmc.Material(10, name='Top nozzle region')
    top_nozzle.set_density('g/cm3', 1.746)
    top_nozzle.add_nuclide("H1", 0.0358870, 'wo')
    top_nozzle.add_nuclide("O16", 0.2847761, 'wo')
    top_nozzle.add_nuclide("B10", 1.15699e-4, 'wo')
    top_nozzle.add_nuclide("B11", 5.27075e-4, 'wo')
    top_nozzle.add_nuclide("Fe54", 0.02644016154, 'wo')
    top_nozzle.add_nuclide("Fe56", 0.43037146399, 'wo')
    top_nozzle.add_nuclide("Fe57", 0.0101152584, 'wo')
    top_nozzle.add_nuclide("Fe58", 0.00137211607, 'wo')
    top_nozzle.add_nuclide("Ni58", 0.04104621835, 'wo')
    top_nozzle.add_nuclide("Mn55", 0.0135739, 'wo')
    top_nozzle.add_nuclide("Cr52", 0.107931450781, 'wo')
    top_nozzle.add_s_alpha_beta('c_H_in_H2O')

    top_fa = openmc.Material(11, name='Top of fuel assemblies')
    top_fa.set_density('g/cm3', 3.044)
    top_fa.add_nuclide("H1", 0.0162913, 'wo')
    top_fa.add_nuclide("O16", 0.1292776, 'wo')
    top_fa.add_nuclide("B10", 5.25228e-5, 'wo')
    top_fa.add_nuclide("B11", 2.39272e-4, 'wo')
    top_fa.add_nuclide("Zr90", 0.43313403903, 'wo')
    top_fa.add_nuclide("Zr91", 0.09549277374, 'wo')
    top_fa.add_nuclide("Zr92", 0.14759527104, 'wo')
    top_fa.add_nuclide("Zr94", 0.15280552077, 'wo')
    top_fa.add_nuclide("Zr96", 0.02511169542, 'wo')
    top_fa.add_s_alpha_beta('c_H_in_H2O')

    bot_fa = openmc.Material(12, name='Bottom of fuel assemblies')
    bot_fa.set_density('g/cm3', 1.762)
    bot_fa.add_nuclide("H1", 0.0292856, 'wo')
    bot_fa.add_nuclide("O16", 0.2323919, 'wo')
    bot_fa.add_nuclide("B10", 9.44159e-5, 'wo')
    bot_fa.add_nuclide("B11", 4.30120e-4, 'wo')
    bot_fa.add_nuclide("Zr90", 0.3741373658, 'wo')
    bot_fa.add_nuclide("Zr91", 0.0824858164, 'wo')
    bot_fa.add_nuclide("Zr92", 0.1274914944, 'wo')
    bot_fa.add_nuclide("Zr94", 0.1319920622, 'wo')
    bot_fa.add_nuclide("Zr96", 0.0216912612, 'wo')
    bot_fa.add_s_alpha_beta('c_H_in_H2O')

    # Define the materials file.
    model.materials = (fuel, clad, cold_water, hot_water, rpv_steel,
                       lower_rad_ref, upper_rad_ref, bot_plate,
                       bot_nozzle, top_nozzle, top_fa, bot_fa)

    ############################################################################################################
    # GEOMETRY

    # Define surfaces.
    s1 = openmc.ZCylinder(R=0.410, surface_id=1)
    s2 = openmc.ZCylinder(R=0.475, surface_id=2)
    s3 = openmc.ZCylinder(R=0.560, surface_id=3)
    s4 = openmc.ZCylinder(R=0.620, surface_id=4)
    s5 = openmc.ZCylinder(R=187.6, surface_id=5)
    s6 = openmc.ZCylinder(R=209.0, surface_id=6)
    s7 = openmc.ZCylinder(R=229.0, surface_id=7)
    s8 = openmc.ZCylinder(R=249.0, surface_id=8, boundary_type='vacuum')

    s31 = openmc.ZPlane(z0=-229.0, surface_id=31, boundary_type='vacuum')
    s32 = openmc.ZPlane(z0=-199.0, surface_id=32)
    s33 = openmc.ZPlane(z0=-193.0, surface_id=33)
    s34 = openmc.ZPlane(z0=-183.0, surface_id=34)
    s35 = openmc.ZPlane(z0=0.000, surface_id=35)
    s36 = openmc.ZPlane(z0=183.0, surface_id=36)
    s37 = openmc.ZPlane(z0=203.0, surface_id=37)
    s38 = openmc.ZPlane(z0=215.0, surface_id=38)
    s39 = openmc.ZPlane(z0=223.0, surface_id=39, boundary_type='vacuum')

    # Define pin cells.
    fuel_cold = openmc.Universe(name='Fuel pin, cladding, cold water', universe_id=1)
    c21 = openmc.Cell(cell_id=21, fill=fuel, region=-s1)
    c22 = openmc.Cell(cell_id=22, fill=clad, region=+s1 & -s2)
    c23 = openmc.Cell(cell_id=23, fill=cold_water, region=+s2)
    fuel_cold.add_cells((c21, c22, c23))

    tube_cold = openmc.Universe(name='Instrumentation guide tube, '
                                     'cold water', universe_id=2)
    c24 = openmc.Cell(cell_id=24, fill=cold_water, region=-s3)
    c25 = openmc.Cell(cell_id=25, fill=clad, region=+s3 & -s4)
    c26 = openmc.Cell(cell_id=26, fill=cold_water, region=+s4)
    tube_cold.add_cells((c24, c25, c26))

    fuel_hot = openmc.Universe(name='Fuel pin, cladding, hot water', universe_id=3)
    c27 = openmc.Cell(cell_id=27, fill=fuel, region=-s1)
    c28 = openmc.Cell(cell_id=28, fill=clad, region=+s1 & -s2)
    c29 = openmc.Cell(cell_id=29, fill=hot_water, region=+s2)
    fuel_hot.add_cells((c27, c28, c29))

    tube_hot = openmc.Universe(name='Instrumentation guide tube, hot water', universe_id=4)
    c30 = openmc.Cell(cell_id=30, fill=hot_water, region=-s3)
    c31 = openmc.Cell(cell_id=31, fill=clad, region=+s3 & -s4)
    c32 = openmc.Cell(cell_id=32, fill=hot_water, region=+s4)
    tube_hot.add_cells((c30, c31, c32))

    # Set positions occupied by guide tubes
    tube_x = np.array([5, 8, 11, 3, 13, 2, 5, 8, 11, 14, 2, 5, 8, 11, 14,
                       2, 5, 8, 11, 14, 3, 13, 5, 8, 11])
    tube_y = np.array([2, 2, 2, 3, 3, 5, 5, 5, 5, 5, 8, 8, 8, 8, 8,
                       11, 11, 11, 11, 11, 13, 13, 14, 14, 14])

    # Define fuel lattices.
    NUM_PINS = 17
    PITCH_PIN = 1.26

    l100 = openmc.RectLattice(name='Fuel assembly (lower half)', lattice_id=100)
    l100.lower_left = (-PITCH_PIN * NUM_PINS / 2, -PITCH_PIN * NUM_PINS / 2)
    l100.pitch = (PITCH_PIN, PITCH_PIN)
    l100.universes = np.tile(fuel_cold, (NUM_PINS, NUM_PINS))
    l100.universes[tube_x, tube_y] = tube_cold

    l101 = openmc.RectLattice(name='Fuel assembly (upper half)', lattice_id=101)
    l101.lower_left = (-PITCH_PIN * NUM_PINS / 2, -PITCH_PIN * NUM_PINS / 2)
    l101.pitch = (PITCH_PIN, PITCH_PIN)
    l101.universes = np.tile(fuel_hot, (NUM_PINS, NUM_PINS))
    l101.universes[tube_x, tube_y] = tube_hot

    # Define assemblies.
    fa_cw = openmc.Universe(name='Water assembly (cold)', universe_id=5)
    c50 = openmc.Cell(cell_id=50, fill=cold_water, region=+s34 & -s35)
    fa_cw.add_cell(c50)

    fa_hw = openmc.Universe(name='Water assembly (hot)', universe_id=7)
    c70 = openmc.Cell(cell_id=70, fill=hot_water, region=+s35 & -s36)
    fa_hw.add_cell(c70)

    fa_cold = openmc.Universe(name='Fuel assembly (cold)', universe_id=6)
    c60 = openmc.Cell(cell_id=60, fill=l100, region=+s34 & -s35)
    fa_cold.add_cell(c60)

    fa_hot = openmc.Universe(name='Fuel assembly (hot)', universe_id=8)
    c80 = openmc.Cell(cell_id=80, fill=l101, region=+s35 & -s36)
    fa_hot.add_cell(c80)

    # Define core lattices
    PITCH_ASSEMBLY = 21.42

    l200 = openmc.RectLattice(name='Core lattice (lower half)', lattice_id=200)
    l200.lower_left = (-PITCH_ASSEMBLY * 21 / 2, -PITCH_ASSEMBLY * 21 / 2)
    l200.pitch = (PITCH_ASSEMBLY, PITCH_ASSEMBLY)
    l200.universes = [
        [fa_cw] * 21,
        [fa_cw] * 21,
        [fa_cw] * 7 + [fa_cold] * 7 + [fa_cw] * 7,
        [fa_cw] * 5 + [fa_cold] * 11 + [fa_cw] * 5,
        [fa_cw] * 4 + [fa_cold] * 13 + [fa_cw] * 4,
        [fa_cw] * 3 + [fa_cold] * 15 + [fa_cw] * 3,
        [fa_cw] * 3 + [fa_cold] * 15 + [fa_cw] * 3,
        [fa_cw] * 2 + [fa_cold] * 17 + [fa_cw] * 2,
        [fa_cw] * 2 + [fa_cold] * 17 + [fa_cw] * 2,
        [fa_cw] * 2 + [fa_cold] * 17 + [fa_cw] * 2,
        [fa_cw] * 2 + [fa_cold] * 17 + [fa_cw] * 2,
        [fa_cw] * 2 + [fa_cold] * 17 + [fa_cw] * 2,
        [fa_cw] * 2 + [fa_cold] * 17 + [fa_cw] * 2,
        [fa_cw] * 2 + [fa_cold] * 17 + [fa_cw] * 2,
        [fa_cw] * 3 + [fa_cold] * 15 + [fa_cw] * 3,
        [fa_cw] * 3 + [fa_cold] * 15 + [fa_cw] * 3,
        [fa_cw] * 4 + [fa_cold] * 13 + [fa_cw] * 4,
        [fa_cw] * 5 + [fa_cold] * 11 + [fa_cw] * 5,
        [fa_cw] * 7 + [fa_cold] * 7 + [fa_cw] * 7,
        [fa_cw] * 21,
        [fa_cw] * 21]

    l201 = openmc.RectLattice(name='Core lattice (upper half)', lattice_id=201)
    l201.lower_left = (-PITCH_ASSEMBLY * 21 / 2, -PITCH_ASSEMBLY * 21 / 2)
    l201.pitch = (PITCH_ASSEMBLY, PITCH_ASSEMBLY)
    l201.universes = [
        [fa_hw] * 21,
        [fa_hw] * 21,
        [fa_hw] * 7 + [fa_hot] * 7 + [fa_hw] * 7,
        [fa_hw] * 5 + [fa_hot] * 11 + [fa_hw] * 5,
        [fa_hw] * 4 + [fa_hot] * 13 + [fa_hw] * 4,
        [fa_hw] * 3 + [fa_hot] * 15 + [fa_hw] * 3,
        [fa_hw] * 3 + [fa_hot] * 15 + [fa_hw] * 3,
        [fa_hw] * 2 + [fa_hot] * 17 + [fa_hw] * 2,
        [fa_hw] * 2 + [fa_hot] * 17 + [fa_hw] * 2,
        [fa_hw] * 2 + [fa_hot] * 17 + [fa_hw] * 2,
        [fa_hw] * 2 + [fa_hot] * 17 + [fa_hw] * 2,
        [fa_hw] * 2 + [fa_hot] * 17 + [fa_hw] * 2,
        [fa_hw] * 2 + [fa_hot] * 17 + [fa_hw] * 2,
        [fa_hw] * 2 + [fa_hot] * 17 + [fa_hw] * 2,
        [fa_hw] * 3 + [fa_hot] * 15 + [fa_hw] * 3,
        [fa_hw] * 3 + [fa_hot] * 15 + [fa_hw] * 3,
        [fa_hw] * 4 + [fa_hot] * 13 + [fa_hw] * 4,
        [fa_hw] * 5 + [fa_hot] * 11 + [fa_hw] * 5,
        [fa_hw] * 7 + [fa_hot] * 7 + [fa_hw] * 7,
        [fa_hw] * 21,
        [fa_hw] * 21]

    # Define root universe.
    root = openmc.Universe(universe_id=0, name='root universe')
    c1 = openmc.Cell(cell_id=1, fill=l200, region=-s6 & +s34 & -s35)
    c2 = openmc.Cell(cell_id=2, fill=l201, region=-s6 & +s35 & -s36)
    c3 = openmc.Cell(cell_id=3, fill=bot_plate, region=-s7 & +s31 & -s32)
    c4 = openmc.Cell(cell_id=4, fill=bot_nozzle, region=-s5 & +s32 & -s33)
    c5 = openmc.Cell(cell_id=5, fill=bot_fa, region=-s5 & +s33 & -s34)
    c6 = openmc.Cell(cell_id=6, fill=top_fa, region=-s5 & +s36 & -s37)
    c7 = openmc.Cell(cell_id=7, fill=top_nozzle, region=-s5 & +s37 & -s38)
    c8 = openmc.Cell(cell_id=8, fill=upper_rad_ref, region=-s7 & +s38 & -s39)
    c9 = openmc.Cell(cell_id=9, fill=bot_nozzle, region=+s6 & -s7 & +s32 & -s38)
    c10 = openmc.Cell(cell_id=10, fill=rpv_steel, region=+s7 & -s8 & +s31 & -s39)
    c11 = openmc.Cell(cell_id=11, fill=lower_rad_ref, region=+s5 & -s6 & +s32 & -s34)
    c12 = openmc.Cell(cell_id=12, fill=upper_rad_ref, region=+s5 & -s6 & +s36 & -s38)
    root.add_cells((c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12))

    # Assign root universe to geometry
    model.geometry.root_universe = root

    ############################################################################################################
    # MESH

    mesh = openmc.Mesh(mesh_id=1)
    mesh.type = 'regular'
    mesh.dimension = (1000, 1000, 1)
    mesh.lower_left = (-229.0, -229.0, -229.0)
    mesh.upper_right = (229.0, 229.0, 229.0)

    # Create a mesh filter
    mesh_filter = openmc.MeshFilter(mesh)

    ############################################################################################################
    # CROSS-SECTION LIBRARY

    energy_groups = openmc.mgxs.EnergyGroups()
    energy_bounds = np.logspace(-3, 7.3, 21)
    energy_groups.group_edges = energy_bounds

    energy_filter = openmc.EnergyFilter(np.logspace(-3, 7.3, 1000))

    # Instantiate a 1-group EnergyGroups object
    one_group = openmc.mgxs.EnergyGroups()
    one_group.group_edges = np.array([energy_groups.group_edges[0], energy_groups.group_edges[-1]])

    # Initialize an 20-energy-group and 6-delayed-group MGXS Library
    mgxs_lib = openmc.mgxs.Library(model.geometry)
    mgxs_lib.energy_groups = energy_groups
    mgxs_lib.num_delayed_groups = 6

    # Specify multi-group cross section types to compute
    mgxs_lib.mgxs_types = ['total', 'transport', 'nu-scatter matrix', 'kappa-fission', 'inverse-velocity', 'chi-prompt',
                           'prompt-nu-fission', 'chi-delayed', 'delayed-nu-fission', 'beta']
    # Specify a "mesh" domain type for the cross section tally filters
    mgxs_lib.domain_type = 'mesh'
    # Specify the mesh domain over which to compute multi-group cross sections
    mgxs_lib.domains = [mesh]

    # Construct all tallies needed for the multi-group cross section library
    mgxs_lib.build_library()

    ############################################################################################################
    # TALLIES

    # Create a "tallies.xml" file for the MGXS Library
    model.tallies = openmc.Tallies()
    mgxs_lib.add_to_tallies_file(model.tallies, merge=True)

    # Instantiate a flux tally; Other valid options: 'current', 'fission', etc
    flux_tally = openmc.Tally(name='Mesh')
    flux_tally.filters = [mesh_filter]
    flux_tally.scores = ['flux']

    energy_tally = openmc.Tally(name='Energy')
    energy_tally.filters = [energy_filter]
    energy_tally.scores = ['flux']

    # Add tallies to the tallies file
    model.tallies.append(flux_tally)
    model.tallies.append(energy_tally)

    ############################################################################################################
    # SETTINGS

    model.settings.batches = 45
    model.settings.inactive = 5
    model.settings.particles = 5000
    uniform_dist = openmc.stats.Box([-160, -160, -183], [160, 160, 183], only_fissionable=False)
    model.settings.source = openmc.Source(space=uniform_dist)
    # to track particles 3 and 4 from batch 1 and generation 2:
    # model.settings.track = (1, 2, 3, 1, 2, 4)

    ############################################################################################################
    # PLOT

    plot = openmc.Plot().from_geometry(model.geometry)
    plot.filename = 'Full-Core'
    plot.pixels = (3000, 3000)
    plot.basis = 'xy'
    plot.color_by = 'material'
    model.plots.append(plot)

    openmc.plot_geometry(output=True)

    ############################################################################################################

    return model


##########################################
# plt.plot(sp.k_generation)
# plt.plot(sp.entropy)


def flux_spectrum(statepoint_file, desired_score=''):
    sp = openmc.StatePoint(filename=statepoint_file)

    flux = sp.get_tally(name='Energy').get_slice(scores=['flux'])
    df = flux.get_pandas_dataframe()
    fluxes = df['mean'].values
    fluxes = np.delete(fluxes, 0)

    # Extract the energy bins from the Tally's EnergyFilter
    energy_filter = flux.find_filter(openmc.EnergyFilter)
    energies = energy_filter.bins
    energies = np.delete(energies, [0, 1])

    print(len(energies))
    print(energies)
    print(len(fluxes))
    print(fluxes)

    return energies, fluxes


# https://openmc.readthedocs.io/en/stable/io_formats/statepoint.html#io-statepoint
def statepoint_evaluation(statepoint_file, desired_score=''):
    sp = openmc.StatePoint(filename=statepoint_file)

    # Initialize MGXS Library with OpenMC statepoint data
    # xs_lib.load_from_statepoint(sp)

    # Extract the current tally separately
    # current_tally = sp.get_tally(name='current tally')

    score_df = sp.get_tally(name='Mesh').get_slice(scores=['flux']).get_pandas_dataframe()
    print(score_df.head(5).to_string())

    axial_dfs = []

    for i in range(1):
        score_df = score_df[score_df['mesh 1']['z'] == i + 1]
        print(score_df.head(1000).to_string())
        x = score_df['mesh 1']['x']
        y = score_df['mesh 1']['y']
        mean = score_df['mean']

        new_df = pd.DataFrame(list(zip(x, y, mean)), columns=['x', 'y', 'mean'])
        new_df = new_df.pivot(index='y', columns='x', values='mean')

        axial_dfs.append(np.array(new_df.values))

    return axial_dfs


# pwr_core().export_to_xml()
# pwr_core().geometry.export_to_xml()
# pwr_core().materials.export_to_xml()
# pwr_core().settings.export_to_xml()
# pwr_core().plots.export_to_xml()
# pwr_core().tallies.export_to_xml()
#
# im = Image.open(".ppm")
# im.save(".png")

# pwr_assembly().export_to_xml()

pwr_core().export_to_xml()
openmc.run(output=True)

axial_dfs = statepoint_evaluation('statepoint.45.h5')
energy, spectrum = flux_spectrum('statepoint.45.h5')

plot = True
if plot:
    ##################################################################
    data_1 = [go.Scatter(x=energy,
                         y=spectrum,
                         mode='lines',
                         marker=dict(line=dict(width=1))
                         )]

    layout_1 = dict(title='Test',
                    width=1500,
                    height=1000,
                    xaxis=dict(type='log'),
                    yaxis=dict(type='log'),
                    )

    figure_1 = dict(data=data_1, layout=layout_1)
    plotly.offline.plot(figure_1, filename='file1.html')

    ##################################################################
    # Instantiate Data
    data = [go.Surface(
        # z=np.zeros(np.shape(axial_dfs[0])),
        z=axial_dfs[0],
        surfacecolor=axial_dfs[0],
        colorscale='RdBu',
    )]

    # Layout
    layout = dict(title='Test',
                  hovermode='closest',
                  width=1500,
                  height=1000,
                  scene=dict(
                      # xaxis=dict(range=[-10, 100]),
                      # yaxis=dict(range=[-10, 100]),
                      zaxis=dict(range=[0, .005])),
                  )

    figure = dict(data=data, layout=layout)
    plotly.offline.plot(figure, filename='file.html')
    ##################################################################

# if plot:
#
#     maxes = []
#     for m in range(len(axial_dfs)):
#         c_max = np.amax(np.array(axial_dfs[m]))
#         maxes.append(c_max)
#     c_max = np.max(np.array(maxes))
#
#     # Instantiate Data
#     data = [go.Surface(z=np.zeros(np.shape(axial_dfs[0])),
#                        surfacecolor=axial_dfs[0],
#                        cmax=c_max,
#                        cmin=0,
#                        colorscale='Viridis',
#                        )]
#
#     ###############################################
#
#     # Instantiate Frames
#     frames = []
#     steps = []
#     for k in range(len(axial_dfs)):
#         frame_data = go.Surface(z=np.full(np.shape(axial_dfs[0]), k),
#                                 surfacecolor=axial_dfs[k]
#                                 )
#         frame = dict(data=[frame_data], name='Axial Step {}'.format(k))
#         frames.append(frame)
#
#         slider_step = dict(args=[
#                 ['Axial Step {}'.format(k)],
#                 dict(frame=dict(duration=0, redraw=False),
#                      mode='immediate',
#                      transition={'duration': 0})
#             ],
#                 label='{}'.format(k),
#                 method='animate')
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
#                         zaxis=dict(range=[0, 10])),
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
#                   # slider=dict(args=[
#                   #               'slider.value', {
#                   #                   'duration': 1000,
#                   #                   'ease': 'cubic-in-out'
#                   #               }
#                   #           ],
#                   #           initialValue=0,
#                   #           plotlycommand='animate',
#                   #           values=np.arange(10),
#                   #           visible=True
#                   #       ),
#                   sliders=[sliders_dict]
#                   )
#
#     figure = dict(data=data, layout=layout, frames=frames)
#
#     ##################################################################
#
#     plotly.offline.plot(figure, filename='file.html')
