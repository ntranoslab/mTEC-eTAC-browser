import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path='/')

layout = html.Div([
    html.Div([
        html.Div([
                html.A(
                html.Img(src='assets/gardner-lab-logo-200w-transparent.png', style={'width': '15%', 'display': 'inline-block'}),
                href = 'https://diabetes.ucsf.edu/lab/gardner-lab',
                target = '_blank'
                ),
                html.Div([
                    dcc.Tabs(id='analyze-tabs', value='mTECs', children=[
                
                    dcc.Tab(label='mTECs', value='mTECs'),
                    dcc.Tab(label='eTACs', value='eTACs'),
                    dcc.Tab(label='Other', value='Other')
                    ])
                ], style = {'float': 'right'}),
            ]),
        html.Div([
            html.H3('Home', id = 'headline'),
        ])
    ], className = 'header'),
])


@callback(
    Output(component_id='analytics-output', component_property='children'),
    Input(component_id='analytics-input', component_property='value')
)
def update_city_selected(input_value):
    return f'You selected: {input_value}'