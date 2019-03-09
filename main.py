import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from parameters import material, geometry, mesh_settings, scoring_xsections, runtime, postprocessing

app.layout = html.Div([
    dcc.Location(id='url', refresh=False, pathname='/parameters/material'),

    # TODO: Storage data not persist through pathname change
    # Materials
    dcc.Store(id='material-stores', storage_type='memory'),
    # Geometry
    dcc.Store(id='color-stores', storage_type='memory'),
    dcc.Store(id='cell-stores', storage_type='memory'),
    dcc.Store(id='injection-stores', storage_type='memory'),
    dcc.Store(id='temp-assembly-stores', storage_type='memory'),
    # dcc.Store(id='assembly-stores', storage_type='session'),
    dcc.Store(id='boundary-stores', storage_type='memory'),
    # Scores
    dcc.Store(id='score-stores', storage_type='memory'),

    dcc.Link('Materials', href='/parameters/material'), html.Br(),
    dcc.Link('Geometry', href='/parameters/geometry'), html.Br(),
    dcc.Link('Mesh and Settings', href='/parameters/mesh_settings'), html.Br(),
    dcc.Link('Scoring and Cross-sections', href='/parameters/scoring_xsections'), html.Br(),
    dcc.Link('Verification and Run', href='/parameters/runtime'), html.Br(),
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

    elif pathname == '/parameters/mesh_settings':
        return mesh_settings.layout

    elif pathname == '/parameters/scoring_xsections':
        return scoring_xsections.layout

    elif pathname == '/parameters/runtime':
        return runtime.layout

    # elif pathname == '/parameters/postprocessing':
        # return postprocessing.layout

    else:
        return '404 Page not Found'


if __name__ == '__main__':
    app.run_server(debug=True)
