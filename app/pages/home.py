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

        html.A(
            html.Button(
                html.Div([
                html.H3('Thymus'),
                html.H4('medullary Thymic Epithelial Cells'),
                html.H5('Explore our data on this cell population that resides in the thymus, a primary lymphoid organ.'),
                ]),
                className='home-buttons'), 
            href = '/mtecs', id='mtec-home-button'),

        html.Img(src='assets/gardnerhero_0.jpeg', id = 'etac-picture', style = {'width': '50%', 'float': 'right'}),
        html.A(
            html.Button(
                html.Div([
                html.H3('Lymph Nodes'),
                html.H4('extraThymic Aire-expressing Cells'),
                html.H5('Explore our data on this cell population that mainly resides in secondary lymphoid organs.'),
                ]),
                className = 'home-buttons'), 
            href = '/etacs', id='etac-home-button'),

        ], className='page-body', style={'height': '100%', 'display': 'flex', 'justify-content': 'center'}),

    
])
