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

    html.Div([
        html.Div([
            html.H4('Required Settings'),
            html.Label('Total Batches'), dcc.Input(id='total-batches', value=100, type='number'),
            html.Label('Inactive Batches'), dcc.Input(id='inactive-batches', value=20, type='number'),
            html.Label('Particles'), dcc.Input(id='particles', value=1000, type='number'),
            html.Label('Generations per Batch'), dcc.Input(id='gens-per-batch', value=10, type='number'),
            html.Label('Seed'), dcc.Input(id='seed', value=1, type='number'),

            html.H4('Miscellaneous'),
            daq.BooleanSwitch(id='trigger-active', label='Trigger Active', labelPosition='right',
                              style=dict(position='absolute', left=0)), html.Br(), html.Br(),
            # keff_trigger = dict
            # trigger_batch_interval = int
            # trigger_max_batches = int

            daq.BooleanSwitch(id='no-reduce', label='No Reduce', labelPosition='right',
                              style=dict(position='absolute', left=0)), html.Br(), html.Br(),
            daq.BooleanSwitch(id='confidence-intervals', label='Confidence Intervals', labelPosition='right', on=False,
                              style=dict(position='absolute', left=0)), html.Br(), html.Br(),
            daq.BooleanSwitch(id='ptables', label='P-Tables', labelPosition='right', on=False,
                              style=dict(position='absolute', left=0)),
            html.Br(), html.Br(),
            daq.BooleanSwitch(id='run-cmfd', label='Run CMFD', labelPosition='right', on=False,
                              style=dict(position='absolute', left=0)),
            html.Br(), html.Br(),
            daq.BooleanSwitch(id='survival-biasing', label='Survival Biasing', labelPosition='right', on=False,
                              style=dict(position='absolute', left=0)), html.Br(), html.Br(),
            daq.BooleanSwitch(id='fission-neutrons', label='Create Fission Neutrons', labelPosition='right', on=True,
                              style=dict(position='absolute', left=0)), html.Br(), html.Br(),
            # ufs_mesh = openmc.Mesh
            # volume_calculations = iterable of VolumeCalculation
            # resonance_scattering = dict

            # tabular_legendre (dict) – Determines if a multi-group scattering moment kernel expanded via Legendre polynomials
            # is to be converted to a tabular distribution or not. Accepted keys are ‘enable’ and ‘num_points’. The value for
            # ‘enable’ is a bool stating whether the conversion to tabular is performed; the value for ‘num_points’ sets the
            # number of points to use in the tabular distribution, should ‘enable’ be True.

            html.H4('Outputs'),
            daq.BooleanSwitch(id='output-summary', label='Output Summary', labelPosition='right', on=True,
                              style=dict(position='absolute', left=0)), html.Br(), html.Br(),
            daq.BooleanSwitch(id='output-tallies', label='Output Tallies', labelPosition='right', on=True,
                              style=dict(position='absolute', left=0)), html.Br(), html.Br(),
            html.Label('Verbosity'),
            dcc.Slider(id='verbosity', min=0, max=10, step=1, value=7),

            html.Button('Submit Settings to Memory', id='submit-settings-btn', n_clicks=0)
        ], style=dict(
            display='table-cell',
            verticalAlign="top",
            width='25%'
        )),

        html.Div([
            html.Div(style=dict(height=20)),
            html.H4('Run Mode'),
            dcc.Dropdown(id='run-mode', value='eigenvalue', options=[
                {'label': 'Fixed Source', 'value': 'fixed source'},
                {'label': 'Eigenvalue', 'value': 'eigenvalue'},
                {'label': 'Volume', 'value': 'volume'},
                {'label': 'Plot', 'value': 'plot'},
                {'label': 'Particle Restart', 'value': 'particle restart'},
            ]),

            html.H4('Energy Mode'),
            dcc.Dropdown(id='energy-mode', value='continuous-energy', options=[
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

            html.H3('Source Distributions'),
            html.P("""
                Source distributions characterize the initialization of particles. There are three choices:
                Cartesian Independent, Box, and Point. Box is selected by default and it allows the creation
                of particles anywhere in the geometry that there exists fissionable material. OpenMC allows
                for particle initialization in non-fissionable materials but for this scope that is non-sensible 
                thus particles will only be initialized in fissionable materials. *Describe Cartesian Independent 
                and Point once implemented*
                   """),
            dcc.Dropdown(id='stats-spatial', value='box', options=[
                {'label': 'Cartesian Independent', 'value': 'cartesian-independent'},
                {'label': 'Box', 'value': 'box'},
                {'label': 'Point', 'value': 'point'},
            ]),
            html.Label('Whole Geometry'),
            daq.BooleanSwitch(id='whole-geometry', on=True, style=dict(float='left')),
            html.P('If whole geometry is on, this means that a box distribution will occupy the whole geometry'),
            html.Br(),

            html.Div([
                html.Label('Lower x'),
                daq.NumericInput(id='box-lower-x',
                                 value=0,
                                 size=150,
                                 ),
                html.Label('Lower y'),
                daq.NumericInput(id='box-lower-y',
                                 value=0,
                                 size=150,
                                 ),
                html.Label('Lower z'),
                daq.NumericInput(id='box-lower-z',
                                 value=0,
                                 size=150,
                                 ),
                html.Label('Upper x'),
                daq.NumericInput(id='box-upper-x',
                                 value=0,
                                 size=150,
                                 ),
                html.Label('Upper y'),
                daq.NumericInput(id='box-upper-y',
                                 value=0,
                                 size=150,
                                 ),
                html.Label('Upper z'),
                daq.NumericInput(id='box-upper-z',
                                 value=0,
                                 size=150,
                                 ),
            ], id='source-bounds'),

            html.H4('Angular Distributions'),
            dcc.Dropdown(id='stats-angular', value='isotropic', options=[
                {'label': 'No Angular Specification', 'value': None},
                {'label': 'Polar Azimuthal', 'value': 'polar-azimuthal'},
                # Parameters: mu (openmc.stats.Univariate) – Distribution of the cosine of the polar angle
                #             phi (openmc.stats.Univariate) – Distribution of the azimuthal angle in radians
                #             reference_uvw (Iterable of float)

                {'label': 'Isotropic', 'value': 'isotropic'},
                # Parameters: None

                {'label': 'Mono-Directional', 'value': 'mono-directional'},
                # Parameters: reference_uvw (Iterable of float) – Direction from which polar angle is measured.
                #                                                 Defaults to the positive x-direction.
            ]),
            html.Div([
                html.Label('Reference U'),
                daq.NumericInput(id='reference-u',
                                 value=0,
                                 size=150,
                                 ),
                html.Label('Reference V'),
                daq.NumericInput(id='reference-v',
                                 value=0,
                                 size=150,
                                 ),
                html.Label('Reference W'),
                daq.NumericInput(id='reference-w',
                                 value=0,
                                 size=150,
                                 ),
            ], id='reference-uvw'),
            html.Br(),

            dcc.RadioItems(id='mu-or-phi', value=None, options=[
                {'label': 'Mu', 'value': 'mu'},
                {'label': 'Phi', 'value': 'phi'}
            ]),

            html.Div([
                html.Label('Probability Distributions'),
                dcc.Dropdown(id='stats-probability', value='discrete', options=[
                    {'label': 'Discrete', 'value': 'discrete'},
                    {'label': 'Uniform', 'value': 'uniform'},
                    {'label': 'Maxwell', 'value': 'maxwell'},
                    {'label': 'Watt', 'value': 'watt'},
                    {'label': 'Tabular', 'value': 'tabular'},
                    {'label': 'Legendre', 'value': 'legendre'},
                    {'label': 'Mixture', 'value': 'mixture'},
                ]),

                html.Div([
                    html.H6('Discrete Parameters'),
                    html.Label('Values'),
                    dcc.Input(id='angle-discrete-values', placeholder='Comma separated list of values'),
                    html.Label('Probabilities'),
                    dcc.Input(id='angle-discrete-probs', placeholder='Comma separated list of probabilities')
                ], id='angle-discrete-params'),

                html.Div([
                    html.H6('Uniform Parameters'),
                    html.Label('a'),
                    daq.NumericInput(id='angle-uniform-a', value=0, size=150),
                    html.Label('b'),
                    daq.NumericInput(id='angle-uniform-b', value=0, size=150),
                ], id='angle-uniform-params'),

                html.Div([
                    html.H6('Maxwell Parameters'),
                    html.Label('Temperature'),
                    daq.NumericInput(id='angle-maxwell-t', value=0, size=150),
                ], id='angle-maxwell-params'),

                html.Div([
                    html.H6('Watt Parameters'),
                    html.Label('a'),
                    daq.NumericInput(id='angle-watt-a', value=0, size=150),
                    html.Label('b'),
                    daq.NumericInput(id='angle-watt-b', value=0, size=150),
                ], id='angle-watt-params'),

                html.Div([
                    html.H6('Tabular Parameters'),
                    html.Label('Values'),
                    dcc.Input(id='angle-tabular-values', placeholder='Comma separated list of values'),
                    html.Label('Probabilities'),
                    dcc.Input(id='angle-tabular-probs', placeholder='Comma separated list of probabilities'),
                    dcc.Dropdown(id='angle-interpolation', value='linear-linear', options=[
                        {'label': 'Histogram', 'value': 'histogram'},
                        {'label': 'Linear-Linear', 'value': 'linear-linear'},
                        {'label': 'Linear-Logarithmic', 'value': 'linear-log'},
                        {'label': 'Logarithmic-Linear', 'value': 'log-linear'},
                        {'label': 'Logarithmic-Logarithmic', 'value': 'log-log'},
                    ])
                ], id='angle-tabular-params'),

                html.Div([
                    html.H6('Legendre Parameters'),
                    html.Label('Legendre Polynomial Coefficients'),
                    dcc.Input(id='angle-legendre-coeffs', placeholder='Comma separated list of coefficients'),
                ], id='angle-legendre-params'),

                # Mixture Parameters
                # TODO

                html.Br(),
                html.Button('Submit Probability to Mu/Phi', id='submit-prob-mu-phi')

            ], id='angular-probability'),

            html.H4('Energy Distributions'),
            dcc.Dropdown(id='stats-energy', value=None, options=[
                {'label': 'No Energy Specification', 'value': None},
                {'label': 'Discrete', 'value': 'discrete'},
                {'label': 'Uniform', 'value': 'uniform'},
                {'label': 'Maxwell', 'value': 'maxwell'},
                {'label': 'Watt', 'value': 'watt'},
                {'label': 'Tabular', 'value': 'tabular'},
                {'label': 'Legendre', 'value': 'legendre'},
                {'label': 'Mixture', 'value': 'mixture'},
            ]),
            html.Label('Source Strength'),
            dcc.Slider(id='source-strength', value=1.0, min=0, max=10, step=0.1),

            html.Br(),
            html.Label('Source Name'),
            dcc.Input(id='source-name', placeholder='Source Name'),
            html.Button('Add Source', id='add-source-btn'),

            html.H3('List of Sources'),
            dcc.Dropdown(id='source-dropdown'),

            # model.settings.entropy_mesh = openmc.mesh
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

        ], style=dict(
            display='table-cell',
            verticalAlign="top",
            width='75%'
        ))
    ],
        style=dict(
            width='100%',
            display='table',
        )),
]),


#######################################################################################################################
# Settings Interface

@app.callback(
    Output('source-bounds', 'style'),
    [Input('whole-geometry', 'on')]
)
def hide_bounds(on):
    if on:
        return dict(display='none')
    else:
        return None


@app.callback(
    [Output('mu-or-phi', 'style'),
     Output('reference-uvw', 'style')],
    [Input('stats-angular', 'value')]
)
def hide_elements(source_angular):
    if source_angular == 'polar-azimuthal':
        return dict(), dict()

    elif source_angular == 'mono-directional':
        return dict(display='none'), dict()

    elif source_angular == 'isotropic':
        return dict(display='none'), dict(display='none')

    else:
        return dict(display='none'), dict(display='none')


@app.callback(
    Output('angular-probability', 'style'),
    [Input('mu-or-phi', 'value')]
)
def hide_elements(mu_or_phi):
    if mu_or_phi:
        return dict()
    else:
        return dict(display='none')


@app.callback(
    [Output('angle-discrete-params', 'style'),
     Output('angle-uniform-params', 'style'),
     Output('angle-maxwell-params', 'style'),
     Output('angle-watt-params', 'style'),
     Output('angle-tabular-params', 'style'),
     Output('angle-legendre-params', 'style')],
    [Input('stats-probability', 'value')]
)
def hide_elements(probability_type):
    if probability_type == 'discrete':
        return dict(), dict(display='none'), dict(display='none'), dict(display='none'), dict(display='none'), dict(
            display='none'),

    elif probability_type == 'uniform':
        return dict(display='none'), dict(), dict(display='none'), dict(display='none'), dict(display='none'), dict(
            display='none'),

    elif probability_type == 'maxwell':
        return dict(display='none'), dict(display='none'), dict(), dict(display='none'), dict(display='none'), dict(
            display='none'),

    elif probability_type == 'watt':
        return dict(display='none'), dict(display='none'), dict(display='none'), dict(), dict(display='none'), dict(
            display='none'),

    elif probability_type == 'tabular':
        return dict(display='none'), dict(display='none'), dict(display='none'), dict(display='none'), dict(), dict(
            display='none'),

    elif probability_type == 'legendre':
        return dict(display='none'), dict(display='none'), dict(display='none'), dict(display='none'), dict(
            display='none'), dict(),


@app.callback(
    Output('mu-phi-stores', 'data'),
    [Input('submit-prob-mu-phi', 'n_clicks')],
    [State('mu-or-phi', 'value'),

     State('stats-probability', 'value'),

     State('angle-discrete-values', 'value'),
     State('angle-discrete-probs', 'probs'),

     State('angle-uniform-a', 'value'),
     State('angle-uniform-b', 'value'),

     State('angle-maxwell-t', 'value'),

     State('angle-watt-a', 'value'),
     State('angle-watt-b', 'value'),

     State('angle-tabular-values', 'value'),
     State('angle-tabular-probs', 'value'),
     State('angle-interpolation', 'value'),

     State('angle-legendre-coeffs', 'value'),

     State('mu-phi-stores', 'data')]
)
def store_mu_phi_prob(click, mu_or_phi, stats_probability,
                      angle_discrete_values, angle_discrete_probs,
                      angle_uniform_a, angle_uniform_b,
                      angle_maxwell_t,
                      angle_watt_a, angle_watt_b,
                      angle_tabular_values, angle_tabular_probs, angle_tabular_interpolation,
                      angle_legendre_coeffs, mu_phi_data):
    mu_phi_data = mu_phi_data or {}

    if click and mu_or_phi == 'mu':
        mu_phi_data.update({'mu':
                                {'stats-probability': stats_probability,
                                 'angle-discrete-values': angle_discrete_values,
                                 'angle-discrete-probs': angle_discrete_probs,
                                 'angle-uniform-a': angle_uniform_a,
                                 'angle-uniform-b': angle_uniform_b,
                                 'angle-maxwell-t': angle_maxwell_t,
                                 'angle-watt-a': angle_watt_a,
                                 'angle-watt-b': angle_watt_b,
                                 'angle-tabular-values': angle_tabular_values,
                                 'angle-tabular-probs': angle_tabular_probs,
                                 'angle-interpolation': angle_tabular_interpolation,
                                 'angle-legendre-coeffs': angle_legendre_coeffs}
                            })
    if click and mu_or_phi == 'phi':
        mu_phi_data.update({'phi':
                                {'stats-probability': stats_probability,
                                 'angle-discrete-values': angle_discrete_values,
                                 'angle-discrete-probs': angle_discrete_probs,
                                 'angle-uniform-a': angle_uniform_a,
                                 'angle-uniform-b': angle_uniform_b,
                                 'angle-maxwell-t': angle_maxwell_t,
                                 'angle-watt-a': angle_watt_a,
                                 'angle-watt-b': angle_watt_b,
                                 'angle-tabular-values': angle_tabular_values,
                                 'angle-tabular-probs': angle_tabular_probs,
                                 'angle-interpolation': angle_tabular_interpolation,
                                 'angle-legendre-coeffs': angle_legendre_coeffs}
                            })
    return mu_phi_data


@app.callback(
    Output('source-stores', 'data'),
    [Input('add-source-btn', 'n_clicks')],
    [State('source-name', 'value'),

     State('stats-spatial', 'value'),

     State('whole-geometry', 'value'),
     State('box-lower-x', 'value'),
     State('box-lower-y', 'value'),
     State('box-lower-z', 'value'),
     State('box-upper-x', 'value'),
     State('box-upper-y', 'value'),
     State('box-upper-z', 'value'),

     State('stats-angular', 'value'),
     State('reference-u', 'value'),
     State('reference-v', 'value'),
     State('reference-w', 'value'),

     State('mu-phi-stores', 'data'),
     State('source-stores', 'data')]
)
def test(click, source_name, stats_spatial, whole_geometry,
         box_lower_x, box_lower_y, box_lower_z,
         box_upper_x, box_upper_y, box_upper_z,
         stats_angular, reference_u, reference_v, reference_w,
         mu_phi_data, source_data):
    source_data = source_data or {}
    if click:
        source_data.update({'{}'.format(source_name):
                                {'stats-spatial': stats_spatial,
                                 'whole-geometry': whole_geometry,
                                 'box-lower-x': box_lower_x,
                                 'box-lower-y': box_lower_y,
                                 'box-lower-z': box_lower_z,
                                 'box-upper-x': box_upper_x,
                                 'box-upper-y': box_upper_y,
                                 'box-upper-z': box_upper_z,
                                 'stats-angular': stats_angular,
                                 'reference-u': reference_u,
                                 'reference-v': reference_v,
                                 'reference-w': reference_w}
                            })
        if mu_phi_data:
            if 'mu' in mu_phi_data:
                source_data[source_name].update({'mu': mu_phi_data['mu']})

            if 'phi' in mu_phi_data:
                source_data[source_name].update({'phi': mu_phi_data['phi']})

    print(source_data)
    return source_data


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

     State('stats-spatial', 'value'),
     State('stats-angular', 'value'),
     State('stats-energy', 'value'),

     State('trigger-active', 'on'),
     # ...
     State('no-reduce', 'on'),
     State('confidence-intervals', 'on'),
     State('ptables', 'on'),
     State('run-cmfd', 'on'),
     State('survival-biasing', 'on'),
     State('fission-neutrons', 'on'),
     # ...
     State('output-summary', 'on'),
     State('output-tallies', 'on'),
     State('verbosity', 'value'),
     # ...
     State('settings-stores', 'data')]
)
def store_settings(click,
                   total_batches, inactive_batches, particles, gens_per_batch, seed, run_mode, energy_mode, cutoff,
                   temperature_mode, source_space, source_angle, source_energy, trigger_active, no_reduce,
                   confidence_intervals, ptables, run_cmfd,
                   survival_biasing, fission_neutrons, output_summary, output_tallies, verbosity,
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
                              'source-space': source_space,
                              'source-angle': source_angle,
                              'source-energy': source_energy,
                              'trigger-active': trigger_active,
                              'no-reduce': no_reduce,
                              'confidence-intervals': confidence_intervals,
                              'ptables': ptables,
                              'run-cmfd': run_cmfd,
                              'survival-biasing': survival_biasing,
                              'fission-neutrons': fission_neutrons,
                              'output-summary': output_summary,
                              'output-tallies': output_tallies,
                              'verbosity': verbosity}
                             )

    return settings_data
