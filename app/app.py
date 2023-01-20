# Run this app with `python app.py` and
# visit http://localhost:8050/ in your web browser.


import base64
import io

from dash import Dash, dcc, html, Input, Output, State, ctx
import dash
import plotly.express as px
import numpy as np

import pandas as pd

app = Dash(__name__, use_pages=True)
server = app.server

##=========================Page Layout=========================##
app.layout = html.Div([
        dash.page_container,
    ])

##=========================Local development only=========================##
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=8050)

