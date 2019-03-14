import dash
import dash_resumable_upload

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
dash_resumable_upload.decorate_server(app.server, "uploads")
app.config.suppress_callback_exceptions = True
