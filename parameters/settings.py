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
                'color': '#4D637F'
            }),

    html.Br(),

    ###############################################################
    # https://openmc.readthedocs.io/en/stable/pythonapi/generated/openmc.Settings.html#openmc.Settings
    html.H2('Run Settings'),

    html.Label('Total Batches'), dcc.Input(id='total-batches', type='number'),
    html.Label('Inactive Batches'), dcc.Input(id='inactive-batches', type='number'),
    html.Label('Particles'), dcc.Input(id='particles', type='number'),
    html.Label('Generations per Batch'), dcc.Input(id='gens-per-batch', type='number'),
    html.Label('Seed'), dcc.Input(id='seed', type='number'),

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
    dcc.Dropdown(id='cutoff', options=[
        {'label': 'Weight', 'value': 'weight'},
        {'label': 'Average Weight', 'value': 'weight_avg'},
        {'label': 'Energy', 'value': 'energy'},
    ]),

    # restore_object('model').settings.entropy_mesh = openmc.mesh
    # max_order = None or int
    # multipole_library = 'path'
    # cross_sections = '/cross-sections/cross_sections.xml'
    html.H4('Temperature'),
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

    html.H4('Outputs'),
    daq.BooleanSwitch(id='output-cross-sections', label='Output Cross-Sections', labelPosition='right', on=True),
    daq.BooleanSwitch(id='output-summary', label='Output Summary', labelPosition='right', on=True),
    daq.BooleanSwitch(id='output-tallies', label='Output Tallies', labelPosition='right', on=True),
    daq.BooleanSwitch(id='cross-sections', label='Output Cross-Sections', labelPosition='right', on=True),
    dcc.Slider(id='verbosity', min=0, max=10, step=1, value=5),

    # restore_object('model').settings.source = Iterable of openmc.Source
    # restore_object('model').settings.state_point = dict
    # restore_object('model').settings.source_point = dict
    # restore_object('model').settings.threads = int
    # restore_object('model').settings.trace = tuple or list
    # restore_object('model').settings.track = tuple or list

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
