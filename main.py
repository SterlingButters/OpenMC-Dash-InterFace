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
            'position': 'relative',
        },
    ), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),

    # TODO: Storage data not persist through pathname change -> storage_type to 'memory' has no effect
    #  Tabs dont load callbacks, only layouts?

    # Materials
    dcc.Store(id='material-stores', storage_type='session'),
    # Geometry
    dcc.Store(id='color-stores', storage_type='session'),
    dcc.Store(id='cell-stores', storage_type='session'),
    dcc.Store(id='injection-stores', storage_type='session'),
    dcc.Store(id='temp-assembly-stores', storage_type='session'),
    dcc.Store(id='assembly-stores', storage_type='session'),
    dcc.Store(id='geometry-stores', storage_type='session'),
    # Mesh
    dcc.Store(id='mesh-stores', storage_type='session'),
    # Scores
    dcc.Store(id='mesh-score-stores', storage_type='session'),
    # Cross-Sections
    dcc.Store(id='xsection-stores', storage_type='session'),
    # Settings
    dcc.Store(id='mu-phi-stores', storage_type='session'),
    dcc.Store(id='source-stores', storage_type='session'),
    dcc.Store(id='settings-stores', storage_type='session'),

    dcc.Tabs(id="tabs", value='postprocessing', children=[
        dcc.Tab(label='Materials', value='materials'),
        dcc.Tab(label='Geometry', value='geometry'),
        dcc.Tab(label='Mesh, Tallies, and Cross-Sections', value='mesh-tallies-xsections'),
        dcc.Tab(label='Settings', value='settings'),
        dcc.Tab(label='Verification & Run', value='runtime'),
        dcc.Tab(label='PostProcessing', value='postprocessing'),
    ]),

    html.Div(id='page-content'),
])


@app.callback(Output('page-content', 'children'),
              [Input('tabs', 'value')])
def display_page(tab):

    if tab == 'materials':
        return material.layout

    elif tab == 'geometry':
        return geometry.layout

    elif tab == 'settings':
        return settings.layout

    elif tab == 'mesh-tallies-xsections':
        return mesh_tallies_xsections.layout

    elif tab == 'runtime':
        return runtime.layout

    elif tab == 'postprocessing':
        return postprocessing.layout


if __name__ == '__main__':
    app.run_server(debug=True)
