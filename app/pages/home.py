import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, path='/')

layout = html.Div([
    html.Div([
        html.Div([
            html.A(
                html.Img(src='static/gardner-lab-logo-200w-transparent-new.png', id = 'lab-logo'),
                href = 'https://diabetes.ucsf.edu/lab/gardner-lab',
                target = '_blank'
                ),
            ], id = 'lab-logo-link'),
            dcc.Markdown('***Aire*-expressing Cell Atlas**', id = 'headline'),
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
                    # html.A(
                    # html.Button('JCs', className='page-buttons'),
                    # href='/jcs'
                    # ),
                ], id = 'tabs'),
    ], className = 'header'),

    html.Br(),

    html.Div([

        html.A(
            html.Button(
                html.Div([
                #html.Img(src='static/mtecs.png', style = {'width': '50%'}),
                html.H3('Thymus'),
                html.H4('medullary Thymic Epithelial Cells'),
                html.H5('Explore our data on this cell population that resides in the thymus, a primary lymphoid organ.'),
                ]),
                className='home-buttons'), 
            href = '/mtecs', id='mtec-home-button'),

        html.Img(src='static/gardnerhero_0.jpeg', id = 'etac-picture', style = {'width': '50%', 'float': 'right'}),
        html.A(
            html.Button(
                html.Div([
                #html.Img(src='static/etacs.png', style = {'width': '50%'}),
                html.H3('Lymph Nodes'),
                html.H4('extraThymic Aire-expressing Cells'),
                html.H5('Explore our data on this cell population that mainly resides in secondary lymphoid organs.'),
                ]),
                className = 'home-buttons'), 
            href = '/etacs', id='etac-home-button'),

        ], className='page-body', style={'height': '100%', 'display': 'flex', 'justify-content': 'center'}),

    
    ])
