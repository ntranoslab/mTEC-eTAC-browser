import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path='/')

layout = html.Div([
    html.Div([
        html.Div([
            html.A(
                html.Img(src='assets/gardner-lab-logo-200w-transparent.png', id = 'lab-logo'),
                href = 'https://diabetes.ucsf.edu/lab/gardner-lab',
                target = '_blank'
                ),
            ], id = 'lab-logo-link'),
            html.H3('Home', id = 'headline'),
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
                ], id = 'tabs'),
    ], className = 'header'),

    html.Div([

        html.Div([
            html.H3('mTECs'),
            html.H4('medullary Thymic Epithelial Cells'),
            html.Br(),
            html.H5('Explore our data on this cell population that resides in the thymus:'),
            html.A(
                    html.Button('mTECs', className='home-buttons'),
                    href='/mtecs'
                    ),
            ], style={'width': '50%', 'height': '100%', 'display': 'inline-block'}, className = 'home-body'),

        html.Div([

            html.H3('eTACs'),
            html.H4('extraThymic Aire-expressing Cells'),
            html.Br(),
            html.H5('Explore our data on this cell population that mainly resides in secondary lymphoid organs:'),
            html.A(
                    html.Button('eTACs', className='home-buttons'),
                    href='/etacs'
                    ),

            ], style={'width': '50%', 'display': 'inline-block'}, className = 'home-body'),

        ], className='page-body', style={'margin-left': '-3%', 'margin-right': '-3%', 'height': '100%'}),

    
])






