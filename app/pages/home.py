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
                    html.A(
                    html.Button('Home', className='selected-button'),
                    href='/'
                    ),
                    html.A(
                    html.Button('mTECs', className='page-buttons'),
                    href='/mtecs'
                    ),
                    html.A(
                    html.Button('eTACs', className='page-buttons'),
                    href='/etacs'
                    ),
                ], style = {'float': 'right', 'display': 'inline-block'}),
            ]),
        html.Div([
            html.H3('Home', id = 'headline'),
        ])
    ], className = 'header'),

    
])






