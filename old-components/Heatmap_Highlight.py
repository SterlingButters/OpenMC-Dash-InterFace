import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, State, Input

import plotly.graph_objs as go
import numpy as np

app = dash.Dash()
app.config['suppress_callback_exceptions'] = True

#######################################################################################################################

app.layout = html.Div([
    html.Div([
        dcc.Graph(id='graph'),
        dcc.Input(id='planes-list', value=.5, type='number'),
    ])])


@app.callback(
    Output('graph', 'figure'),
    [Input('planes-list', 'value')],
    [State('graph', 'clickData')]
)
def highlight_region(plane, clickData):
    edge = plane
    x = np.linspace(-edge, edge, 250)
    y = np.linspace(-edge, edge, 250)

    regions = []
    cell_hover = []
    for i in x:
        row = []
        text_row = []
        for j in y:

            if np.sqrt(i ** 2 + j ** 2) < plane:
                row.append(4)
                text_row.append('Region 1')

            if np.sqrt(i ** 2 + j ** 2) > plane:
                row.append(9)
                text_row.append('Region 2')

        regions.append(row)
        cell_hover.append(text_row)

    ######################################################
    if clickData is not None:
        if 'points' in clickData:
            point = clickData['points'][0]
            if 'x' in point:
                click_x = point['x']
            if 'y' in point:
                click_y = point['y']

        hilit_regions = []
        if 0 < np.sqrt(click_x ** 2 + click_y ** 2) < plane:
            for row_ in regions:
                for num in row_:
                    hilit_regions.append(5)

        if np.sqrt(click_x ** 2 + click_y ** 2) > plane:
            for row_ in regions:
                for num in row_:
                    hilit_regions.append(10)

        regions = hilit_regions
    ######################################################

    heatmap = go.Heatmap(z=regions, x=x, y=y, hoverinfo='x+y+text', text=cell_hover, opacity=0.5, showscale=False)
    data = [heatmap]
    layout = dict(title='Cell Region Depiction',
                  height=1000,
                  width=1000,
                  )
    figure = dict(data=data, layout=layout)
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
