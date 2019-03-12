import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
from dash.dependencies import Output, State, Input

from app import app

layout = html.Div([

    # Title
    html.H2('Settings Configuration',
            style={
                'position': 'relative',
                'top': '0px',
                'left': '10px',
                'font-family': 'Dosis',
                'display': 'inline',
                'font-size': '4.0rem',
                'color': 'rgb(76, 1, 3)'
            }),

    html.Br(),

    ###############################################################
    # https://openmc.readthedocs.io/en/stable/pythonapi/generated/openmc.Settings.html#openmc.Settings
    html.H2('Run Settings'),

    html.Label('Total Batches'), dcc.Input(id='total-batches', value=100, type='number'),
    html.Label('Inactive Batches'), dcc.Input(id='inactive-batches', value=20, type='number'),
    html.Label('Particles'), dcc.Input(id='particles', value=1000, type='number'),
    html.Label('Generations per Batch'), dcc.Input(id='gens-per-batch', value=10, type='number'),
    html.Label('Seed'), dcc.Input(id='seed', value=1, type='number'),

    html.H4('Run Mode'),
    dcc.Dropdown(id='run-mode', options=[
        {'label': 'Fixed Source', 'value': 'fixed source'},
        {'label': 'Eigenvalue', 'value': 'eigenvalue'},
        {'label': 'Volume', 'value': 'volume'},
        {'label': 'Plot', 'value': 'plot'},
        {'label': 'Particle Restart', 'value': 'particle restart'},
    ]),

    html.H4('Energy Mode'),
    dcc.Dropdown(id='energy-mode', options=[
        {'label': 'Continuous Energy', 'value': 'continuous-energy'},
        {'label': 'Multi-Group', 'value': 'multi-group'},
    ]),
    html.H6('Cutoff'),
    # Dictionary defining weight cutoff and energy cutoff.The dictionary may have three
    # keys, ‘weight’, ‘weight_avg’ and ‘energy’.Value for ‘weight’ should be a float indicating weight
    # cutoff below which particle undergo Russian roulette.Value for ‘weight_avg’ should be a float indicating
    # weight assigned to particles that are not killed after Russian roulette.Value of energy should be a float
    # indicating energy in eV below which particle will be killed.
    dcc.Dropdown(id='cutoff', options=[
        {'label': 'Weight', 'value': 'weight'},
        {'label': 'Average Weight', 'value': 'weight_avg'},
        {'label': 'Energy', 'value': 'energy'},
    ]),

    # restore_object('model').settings.entropy_mesh = openmc.mesh
    # max_order = None or int
    # multipole_library = 'path'

    html.H4('Temperature'),
    # Dictionary that efines a default temperature and method for treating intermediate temperatures at which nuclear
    # data doesn’t exist. Accepted keys are ‘default’, ‘method’, ‘range’, ‘tolerance’, and ‘multipole’. The value for
    # ‘default’ should be a float representing the default temperature in Kelvin. The value for ‘method’ should be
    # ‘nearest’ or ‘interpolation’. If the method is ‘nearest’, ‘tolerance’ indicates a range of temperature within
    # which cross sections may be used. The value for ‘range’ should be a pair a minimum and maximum temperatures which
    # are used to indicate that cross sections be loaded at all temperatures within the range. ‘multipole’ is a boolean
    # indicating whether or not the windowed multipole method should be used to evaluate resolved resonance cross sections.
    dcc.Dropdown(id='temperature-mode', options=[
        {'label': 'Default', 'value': 'default'},
        {'label': 'Method', 'value': 'method'},
        {'label': 'Range', 'value': 'range'},
        {'label': 'Tolerance', 'value': 'tolerance'},
        {'label': 'Multipole', 'value': 'multipole'},
    ]),

    html.H4('Miscellaneous'),
    daq.BooleanSwitch(id='trigger-active', label='Trigger Active', labelPosition='right'),
    # keff_trigger = dict
    # trigger_batch_interval = int
    # trigger_max_batches = int

    daq.BooleanSwitch(id='no-reduce', label='No Reduce', labelPosition='right'),
    daq.BooleanSwitch(id='confidence-intervals', label='Confidence Intervals', labelPosition='right'),
    daq.BooleanSwitch(id='ptables', label='P-Tables', labelPosition='right'),
    daq.BooleanSwitch(id='run-cmfd', label='Run CMFD', labelPosition='right'),
    daq.BooleanSwitch(id='survival-biasing', label='Survival Biasing', labelPosition='right'),
    daq.BooleanSwitch(id='fission-neutrons', label='Create Fission Neutrons', labelPosition='right'),
    # ufs_mesh = openmc.Mesh
    # volume_calculations = iterable of VolumeCalculation
    # resonance_scattering = dict

    # tabular_legendre (dict) – Determines if a multi-group scattering moment kernel expanded via Legendre polynomials
    # is to be converted to a tabular distribution or not. Accepted keys are ‘enable’ and ‘num_points’. The value for
    # ‘enable’ is a bool stating whether the conversion to tabular is performed; the value for ‘num_points’ sets the
    # number of points to use in the tabular distribution, should ‘enable’ be True.

    html.H4('Outputs'),
    daq.BooleanSwitch(id='output-cross-sections', label='Output Cross-Sections', labelPosition='right', on=True),
    daq.BooleanSwitch(id='output-summary', label='Output Summary', labelPosition='right', on=True),
    daq.BooleanSwitch(id='output-tallies', label='Output Tallies', labelPosition='right', on=True),
    daq.BooleanSwitch(id='cross-sections', label='Output Cross-Sections', labelPosition='right', on=True),
    dcc.Slider(id='verbosity', min=0, max=10, step=1, value=5),

    html.Button('Submit Settings to Memory', id='submit-settings-btn', n_clicks=0)
]),


#######################################################################################################################
# Settings Interface


@app.callback(
    Output('settings-stores', 'data'),
    [Input('submit-settings-btn', 'n_clicks')],
    [State('total-batches', 'value'),
     State('inactive-batches', 'value'),
     State('particles', 'value'),
     State('gens-per-batch', 'value'),
     State('seed', 'value'),

     State('run-mode', 'value'),
     State('energy-mode', 'value'),
     State('cutoff', 'value'),
     # ...
     State('temperature-mode', 'value'),

     State('trigger-active', 'on'),
     # ...
     State('no-reduce', 'on'),
     State('confidence-intervals', 'on'),
     State('ptables', 'on'),
     State('run-cmfd', 'on'),
     State('survival-biasing', 'on'),
     State('fission-neutrons', 'on'),
     # ...
     State('output-cross-sections', 'on'),
     State('output-summary', 'on'),
     State('output-tallies', 'on'),
     State('cross-sections', 'on'),
     State('verbosity', 'value'),
     # ...
     State('settings-stores', 'data')]
)
def store_settings(click,
                   total_batches, inactive_batches, particles, gens_per_batch, seed, run_mode, energy_mode, cutoff,
                   temperature_mode, trigger_active, no_reduce, confidence_intervals, ptables, run_cmfd, survival_biasing,
                   fission_neutrons, output_cross_sections, output_summary, output_tallies, cross_sections, verbosity,
                   settings_data):
    settings_data = settings_data or {}

    if click:
        settings_data.update({'total-batches': total_batches,
                              'inactive-batches': inactive_batches,
                              'particles': particles,
                              'gens-per-batch': gens_per_batch,
                              'seed': seed,
                              'run-mode': run_mode,
                              'energy-mode': energy_mode,
                              'cutoff': cutoff,
                              'temperature-mode': temperature_mode,
                              'trigger-active': trigger_active,
                              'no-reduce': no_reduce,
                              'confidence-intervals': confidence_intervals,
                              'ptables': ptables,
                              'run-cmfd': run_cmfd,
                              'survival-biasing': survival_biasing,
                              'fission-neutrons': fission_neutrons,
                              'output-cross-sections': output_cross_sections,
                              'output-summary': output_summary,
                              'output-tallies': output_tallies,
                              'cross-sections': cross_sections,
                              'verbosity': verbosity}
                             )

    return settings_data
