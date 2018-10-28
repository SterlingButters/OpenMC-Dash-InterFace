import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, State, Input

import plotly
import plotly.graph_objs as go

from plotly.offline import init_notebook_mode
import plotly.figure_factory as ff


init_notebook_mode(True)

import numpy as np
# from PIL import Image
#
# im = Image.open("plot_10001.ppm")
# im.save("plot_10001.png")

# app = dash.Dash()
#
# app.layout = html.Div([
#
#     html.Div([
#         dcc.Graph(id='graph'),
#         dcc.Input(id='num', value=200, type='number'),
#
#         dcc.Upload(['Drag and Drop or ',
#                     html.A('Select a File')],
#                    id='upload-xml',
#                    multiple=True,
#                    style={
#                    'width': '100%',
#                    'height': '60px',
#                    'lineHeight': '60px',
#                    'borderWidth': '1px',
#                    'borderStyle': 'dashed',
#                    'borderRadius': '5px',
#                    'textAlign': 'center'
#                    })
#     ]),
# ])
#
# @app.callback(
#     Output(component_id='graph', component_property='figure'),
#     [Input(component_id='num', component_property='value')]
# )
# def update_figure(N):
#
#     trace0 = go.Scatter(
#         x=np.random.randn(N),
#         y=np.random.randn(N) + 2,
#         name='Above',
#         mode='markers',
#     )
#
#     trace1 = go.Scatter(
#         x=np.random.randn(N),
#         y=np.random.randn(N) - 2,
#         name='Below',
#         mode='markers',
#     )
#
#     data = [trace0, trace1]
#
#     layout = dict(title='Styled Scatter',
#                   yaxis=dict(zeroline=False),
#                   xaxis=dict(zeroline=False)
#                   )
#
#     fig = dict(data=data, layout=layout)
#
#     return fig
#
#
# if __name__ == '__main__':
#     app.run_server()

##################################################
# Create cell Heatmap

# planes_list = [2, 3, 4, 5]

# edge = planes_list[-1]
# x = np.linspace(-edge, edge, 250)
# y = np.linspace(-edge, edge, 250)
#
#
# regions = []
# hover = []
# for i in x:
#     row = []
#     text_row = []
#     for j in y:
#
#         if np.sqrt(i ** 2 + j ** 2) < planes_list[0]:
#             row.append(7)                                                   # <- Arbitrary number to adjust color
#             text_row.append('Region 1')
#
#         if np.sqrt(i ** 2 + j ** 2) > planes_list[-1]:
#             row.append(5)                                                   # <- Arbitrary number to adjust color
#             text_row.append('Region {}'.format(len(planes_list)+1))
#
#         for k in range(len(planes_list) - 1):
#             if planes_list[k] < np.sqrt(i**2 + j**2) < planes_list[k+1]:
#                 row.append(k*3)                                             # <- Arbitrary number to adjust color
#                 text_row.append('Region {}'.format(k+2))
#     regions.append(row)
#     hover.append(text_row)
#
# heatmap = go.Heatmap(z=regions, x=x, y=y, hoverinfo='x+y+text', text=hover, opacity=0.5)
# data = [heatmap]
# shapes = []
#
# for plane in planes_list:
#     shape = {
#         'type': 'circle',
#         'x0': -plane,
#         'y0': -plane,
#         'x1': plane,
#         'y1': plane,
#         'line': {
#             'width': 4,
#         },
#         'opacity': 1
#     }
#
#     shapes.append(shape)
#
#
# layout = dict(title='Test',
#               height=1000,
#               width=1000,
#               shapes=shapes)
#
# figure = dict(data=data, layout=layout)
#
# plotly.offline.plot(figure)

##################################################
# Create Assembly Heatmap

assemby_dim_x = 17
assemby_dim_y = 17

list = []
for i in range(assemby_dim_y):
    row = []
    for j in range(assemby_dim_x):
        row.append(1)
    list.append(row)

# Display universe name and location
hover = []
for a in range(assemby_dim_y+1):
    row = []
    for b in range(assemby_dim_x+1):
        row.append('universe')
    hover.append(row)

# Invert Matrices
hover = hover[::-1]
z = list[::-1]

print(np.shape(z))

colorscale = 'Viridis'

pitch_x = 17/assemby_dim_x
pitch_y = 17/assemby_dim_y

planes_list = [.2, .5, .6]
planes_list = planes_list[::-1]

shapes = []

for outer in planes_list:
    color = 'rgb({}, {}, {}'.format(*np.random.uniform(0, 255, 3))
    for a in range(len(list)):
        for b in range(len(list[a])):
                shape = {
                    'type': 'circle',
                    'x0': b*pitch_x - outer/2,
                    'y0': a*pitch_y - outer/2,
                    'x1': b*pitch_x - outer/2 + outer,
                    'y1': a*pitch_y - outer/2 + outer,
                    'fillcolor': color,
                    'opacity': 1
                }

                shapes.append(shape)

layout = dict(
    title='Test',
    height=1000,
    width=1000,

    xaxis=dict(
        range=[-(outer/2 + (pitch_x-outer)/2), pitch_x*assemby_dim_x],
        showgrid=False,
        zeroline=False
    ),
    yaxis=dict(
        range=[-(outer/2 + (pitch_y-outer)/2), pitch_y*assemby_dim_y],
        showgrid=False,
        zeroline=False
    ),
    shapes=shapes,
)

heatmap = go.Heatmap(z=z, hoverinfo='x+y+text', text=hover, opacity=0.5)
data = [heatmap]

figure = dict(data=data, layout=layout)

plotly.offline.plot(figure)
