# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


import base64
import io

from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
import numpy as np

import pandas as pd

app = Dash(__name__)

#df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')
df = None
#df = pd.read_csv('file://localhost/Users/nolanhorner/Documents/UCSF/computer-projects/mTEC-eTAC-atlases/test-data/WT_KO_thymus_subset.csv')

app.layout = html.Div([
    #upload data bar
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id = 'output-data-result'),

    html.Div([
        #dropdown with cell type
        html.Div([
            html.H3('Cell Type:'),
            dcc.Dropdown([], id='cell-type-value')
        ], style={'width': '48%', 'display': 'inline-block'}),
        #dropdown with genotype
        html.Div([
            html.H3('Genotype:'),
            dcc.Dropdown([], id='genotype-value')
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    html.Div([
            html.H3('Gene:'),
            dcc.Dropdown([], id='gene-value')
        ], style={'width': '48%', 'display': 'inline-block'}),
    html.Div([
        html.H3('UMAP'),
        dcc.Graph(figure = px.scatter(x = [0], y=[0]),
            #update_layout(width = 800, height = 800, xaxis={'visible': False, 'showticklabels': False},
            #yaxis={'visible': False, 'showticklabels': False},
            #paper_bgcolor = "black"
            #"rgba(1,24,24,10)"
            id='umap-graphic')
    ])
    

])



def check_file(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            global df
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
    except Exception as e:
        print(e)
        return html.Div([
            html.H5(filename),
            html.H5('File is not a csv.')
        ])

    return html.Div([
        html.H5(filename),
        #html.H6(datetime.datetime.fromtimestamp(date)),

        #dash_table.DataTable(
        #    df.to_dict('records'),
        #    [{'name': i, 'id': i} for i in df.columns]
        #),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        #html.Div('Raw Content'),
        #html.Pre(contents[0:200] + '...', style={
        #    'whiteSpace': 'pre-wrap',
        #    'wordBreak': 'break-all'
        #})
    ])


@app.callback(
    Output ('output-data-result', 'children'),
    Output('cell-type-value', 'options'),
    Output('genotype-value', 'options'),
    Output('gene-value', 'options'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
    #Input('gene-value', 'value')
    )
def update_file(upload_data, filename, gene_value = 'Prr15l'):

    if upload_data is not None:
        #is upload_data in correct format?
        #is upload_data a csv?
        #assign df to csv
        check_file(upload_data, filename)
        cell_type_list = np.insert(df['cell_type'].unique(), 0, 'All')
        genotype_list = np.insert(df['genotype'].unique(), 0, 'All')
        #return html.H5(genotype_list)
        gene_list = list(df.columns.unique())
        #remove unnamed col
        gene_list.remove('Unnamed: 0')
        #remove cell_type col
        gene_list.remove('cell_type')
        #remove genotype col
        gene_list.remove('genotype')
        #remove x col
        gene_list.remove('x')
        #remove y col
        gene_list.remove('y')
        #make gene list into array
        gene_list = np.array(gene_list)
        gene_list = np.insert(gene_list, 0, 'All')
        #return html.H5([gene_list])
        dff = df
        #graph
        fig = px.scatter(dff, x='x',
                    #x coordinates
                     y='y',
                     color = gene_value,
                     hover_name = 'cell_type'
                     #y coordinates
                     #hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name']
                     )
        fig.update_layout(width = 800, height = 800, title = gene_value,
            xaxis={'visible': False, 'showticklabels': False},
            yaxis={'visible': False, 'showticklabels': False},
            #paper_bgcolor = "rgba(0,0,0,0)"
            )

            #fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
        return check_file(upload_data, filename), cell_type_list, genotype_list, gene_list
    return html.Div([
            'No File Uploaded'
        ]), [], [], []


@app.callback(
    Output('umap-graphic', 'figure'),
    Input('cell-type-value', 'value'),
    Input('genotype-value', 'value')
    #Input('gene-value', 'value')
    )
def update_graph(cell_type_value, genotype_value, gene_value = 'Prr15l'):

    if df is not None:
        #filter df to only contain data with chosen genotype
        dff = df[df['genotype'] == genotype_value] if genotype_value != 'All' else df
        #filter df to contain data with chosen cell type
        dff = dff[dff['cell_type'] == cell_type_value] if cell_type_value != 'All' else dff
        fig = px.scatter(dff, x='x',
        #x coordinates
                     y='y',
                     color = gene_value,
                     hover_name = 'cell_type'
                     #y coordinates
                     #hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name']
                     )
        fig.update_layout(width = 800, height = 800, title = gene_value,
            xaxis={'visible': False, 'showticklabels': False},
            yaxis={'visible': False, 'showticklabels': False},
            #paper_bgcolor = "rgba(0,0,0,0)"
            )

            #fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
        return fig
    return px.scatter(x = [0], y=[0])


if __name__ == '__main__':
    app.run_server(debug=True)

