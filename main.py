import dash_core_components as dcc
import dash_html_components as html
import matplotlib
from dash.dependencies import Input, Output

matplotlib.use("Agg")

from app import app
from parameters import material, geometry, settings, mesh_tallies_xsections, runtime, postprocessing

app.layout = html.Div([
    html.Img(
        src="https://cert.tees.tamu.edu/wp-content/uploads/sites/3/2017/11/NUEN_secondary.png",
        className='one columns',
        style={
            'height': '140',
            'width': '800',
            'float': 'right',
            'position': 'relative',
        },
    ),

    dcc.Location(id='url', refresh=False, pathname='/parameters/material'),

    # TODO: Storage data not persist through pathname change -> storage_type to 'memory' has no effect
    # Materials
    dcc.Store(id='material-stores', storage_type='session'),
    # Geometry
    dcc.Store(id='color-stores', storage_type='session'),
    dcc.Store(id='cell-stores', storage_type='session'),
    dcc.Store(id='injection-stores', storage_type='session'),
    dcc.Store(id='temp-assembly-stores', storage_type='session'),
    dcc.Store(id='assembly-stores', storage_type='session'),
    dcc.Store(id='boundary-stores', storage_type='session'),
    # Mesh
    dcc.Store(id='mesh-stores', storage_type='session'),
    # Scores
    dcc.Store(id='mesh-score-stores', storage_type='session'),
    # Cross-Sections
    dcc.Store(id='xsection-stores', storage_type='session'),
    # Settings
    dcc.Store(id='settings-stores', storage_type='session'),

    dcc.Link('Materials', href='/parameters/material'), html.Br(),
    dcc.Link('Geometry', href='/parameters/geometry'), html.Br(),
    dcc.Link('Mesh & Tallies & Cross-Sections', href='/parameters/mesh_tallies_xsections'), html.Br(),
    dcc.Link('Settings', href='/parameters/settings'), html.Br(),
    dcc.Link('Verification & Run', href='/parameters/runtime'), html.Br(),
    dcc.Link('Postprocessing', href='/parameters/postprocessing'), html.Br(),

    html.Div(id='page-content'),
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/parameters/material':
        return material.layout

    elif pathname == '/parameters/geometry':
        return geometry.layout

    elif pathname == '/parameters/settings':
        return settings.layout

    elif pathname == '/parameters/mesh_tallies_xsections':
        return mesh_tallies_xsections.layout

    elif pathname == '/parameters/runtime':
        return runtime.layout

    elif pathname == '/parameters/postprocessing':
        return postprocessing.layout

    else:
        return '404 Page not Found'


if __name__ == '__main__':
    app.run_server(debug=True)
