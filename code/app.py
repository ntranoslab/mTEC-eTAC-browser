# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


import base64
import io

from dash import Dash, dcc, html, Input, Output, State, ctx
import plotly.express as px
import numpy as np

import pandas as pd

app = Dash(__name__)

#df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')
df = None
existing_csv = {'WT_KO_thymus_subset.csv': pd.read_csv('file://localhost/Users/nolanhorner/Documents/UCSF/computer-projects/mTEC-eTAC-atlases/test-data/WT_KO_thymus_subset.csv', index_col=0)}
#pd.read_csv('file://localhost/Users/nolanhorner/Documents/UCSF/computer-projects/mTEC-eTAC-atlases/test-data/WT_KO_thymus_subset.csv')
#['WT_KO_thymus_subset.csv']
#df = pd.read_csv('file://localhost/Users/nolanhorner/Documents/UCSF/computer-projects/mTEC-eTAC-atlases/test-data/WT_KO_thymus_subset.csv')
cell_meta_cols = ['genotype']
analyze_cell_dict = {'mTECs': 'UMAPs', 'eTACs': 'tSNEs'}
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H3('File:'),
            dcc.Dropdown(list(existing_csv.keys()), placeholder = 'Select a file...', id='file-value')
        ], style={'width': '32%', 'display': 'inline-block'}),
        html.Div([
            html.H3('Analyze:'),
            dcc.RadioItems(['mTECs', 'eTACs'], 'mTECs', id='analyze-cell-value')
        ], style={'width': '32%', 'float': 'right', 'display': 'inline-block'}),
            #upload data bar
            dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '30%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                'display': 'inline-block'
            },
            # Allow multiple files to be uploaded
            multiple=False
            ),
        ]),
    
    html.Div(id = 'output-data-result'),
    html.H3('Category:'),
    dcc.RadioItems(cell_meta_cols, cell_meta_cols[0], id='category-value'),

    html.Br(),

    html.Div([
        #dropdown with gene
        html.Div([
            html.H3('Gene:'),
            dcc.Dropdown([], placeholder = 'Select a gene...', id='gene-value')
        ], style={'width': '48%', 'display': 'inline-block'}),
        #dropdown with cell type
        #html.Div([
        #    html.H3('Cell Type:'),
        #    dcc.Dropdown([], placeholder = 'Select a cell type...', id='cell-type-value')
        #], style={'width': '48%', 'display': 'inline-block'}),
        #dropdown with genotype
        html.Div([
            html.H3('Genotype:'),
            dcc.Dropdown([], placeholder = 'Select a genotype...', id='genotype-value')
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    html.Div([
        html.H3('UMAPs', id='graph-name-value'),
        html.Div([
            dcc.Graph(figure = px.scatter(x = [0], y=[0], color_discrete_sequence=['white']).update_layout(
                xaxis={'visible': False, 'showticklabels': False},
                yaxis={'visible': False, 'showticklabels': False},
                plot_bgcolor = "white"),
                #yaxis={'visible': False, 'showticklabels': False},
                #paper_bgcolor = "black"
                #"rgba(1,24,24,10)"
                id='umap-graphic-gene')
        ], style={'width': '38%', 'display': 'inline-block'}),
        html.Div([
            dcc.RangeSlider(min=0, max=20, marks = {'10': '50th (10)'}, value=[0, 20], allowCross = False, vertical = True, verticalHeight = 475, tooltip={'placement': 'right', 'always_visible': True}, id='umap-graphic-gene-slider')
            ], style={'marginBottom': '60px',
                    'marginLeft': '150px',
                    'display': 'inline-block'}),
        html.Div([
            dcc.Graph(figure = px.scatter(x = [0], y=[0], color_discrete_sequence=['white']).update_layout(
                xaxis={'visible': False, 'showticklabels': False},
                yaxis={'visible': False, 'showticklabels': False},
                plot_bgcolor = "white"),
                #update_layout(width = 800, height = 800, xaxis={'visible': False, 'showticklabels': False},
                #yaxis={'visible': False, 'showticklabels': False},
                #paper_bgcolor = "black",
                #"rgba(1,24,24,10)"
                id='umap-graphic-cell-types')
            ], style={'width': '38%', 'float': 'right', 'display': 'inline-block'}),
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
                io.StringIO(decoded.decode('utf-8')), index_col = 0)
            if filename not in list(existing_csv.keys()):
                existing_csv[filename] = df
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
    #Output('cell-type-value', 'options'),
    Output('file-value', 'options'),
    Output('file-value', 'value'),
    Output('genotype-value', 'options'),
    Output('gene-value', 'options'),
    Input('file-value', 'value'),
    Input('upload-data', 'contents'),
    #Input('file-value', 'contents'),
    State('upload-data', 'filename')
    #Input('gene-value', 'value')
    )
def update_file(file_value, upload_data, filename):

    input_id = ctx.triggered_id
    #print(input_id)
    global df
    if upload_data is None and file_value is None:
        return html.Div([
            'No File Uploaded'
        ]), list(existing_csv.keys()), '', [], []
    elif input_id == 'file-value':
        df = existing_csv.get(file_value, 'No such file exists')
    elif input_id == 'upload-data':
        #is upload_data in correct format?
        #is upload_data a csv?
        #assign df to csv
        check_file(upload_data, filename)
        if filename in list(existing_csv.keys()):
            file_value = filename
    #cell_type_list = np.insert(df['cell_type'].unique(), 0, 'All')
    genotype_list = np.insert(df['genotype'].unique(), 0, 'All')
    #return html.H5(genotype_list)
    gene_list = list(df.columns.unique())
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
    #gene_list = np.insert(gene_list, 0, 'All')
    #return html.H5([gene_list])
    dff = df
    #graph
    #fig = px.scatter(dff, x='x',
                #x coordinates
                 #y='y',
                 #color = gene_value if gene_value != None else '',
                 #hover_name = 'cell_type'
                 #y coordinates
                 #hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name']
                 #)
    #fig.update_layout(width = 800, height = 800, title = 'Select a gene',
        #xaxis={'visible': False, 'showticklabels': False},
        #yaxis={'visible': False, 'showticklabels': False},
        #paper_bgcolor = "rgba(0,0,0,0)"
        #)

        #fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    return html.Div([
        html.H5(file_value),
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
    ]), list(existing_csv.keys()), file_value, genotype_list, gene_list
    

@app.callback(
    Output('umap-graphic-gene', 'figure'),
    Output('umap-graphic-cell-types', 'figure'),
    Output('genotype-value', 'value'),
    Output('umap-graphic-gene-slider', 'min'),
    Output('umap-graphic-gene-slider', 'max'),
    Output('umap-graphic-gene-slider', 'marks'),
    Output('umap-graphic-gene-slider', 'value'),
    Output('graph-name-value', 'children'),
    #Input('cell-type-value', 'value'),
    Input('genotype-value', 'value'),
    Input('gene-value', 'value'),
    Input('umap-graphic-gene-slider', 'value'),
    Input('analyze-cell-value', 'value')
    #State('umap-graphic-gene-slider', 'value')
    )
def update_graph(genotype_value, gene_value, umap_graphic_gene_slider, analyze_cell_value):
    #check gene_value is part of csv
    #gene_value is text field
    input_id = ctx.triggered_id
    if df is not None:
        #filter df to only contain data with chosen genotype
        if genotype_value is None:
            genotype_value = 'All'
        dff = df[df['genotype'] == genotype_value] if genotype_value != 'All' else df
        #filter df to contain data with chosen cell type
        #dff = dff[dff['cell_type'] == cell_type_value] if cell_type_value != 'All' else dff
        dff = dff[[gene_value, 'cell_type', 'genotype', 'x', 'y']] if gene_value != None else dff
        percentile_values = np.quantile(dff[gene_value], [0.99, 0.01, 0.95, 0.05, 0.90, 0.10, 0.5])
        df_gene_min = min(dff[gene_value])
        df_gene_max = max(dff[gene_value])
        lower_slider_value = percentile_values[1] if input_id == 'gene-value' else min(umap_graphic_gene_slider)
        higher_slider_value = percentile_values[0] if input_id == 'gene-value' else max(umap_graphic_gene_slider)

        gene_fig = px.scatter(dff,
                     #x coordinates
                     x='x',
                     #y coordinates
                     y='y',
                     color = gene_value,
                     hover_name = 'cell_type',
                     range_color=
                     #min of color range
                     [lower_slider_value  if input_id != 'umap-graphic-gene-slider' else min(umap_graphic_gene_slider), 
                     #max of color range
                     higher_slider_value  if input_id != 'umap-graphic-gene-slider' else max(umap_graphic_gene_slider)]
                     )
        gene_fig.update_layout(width = 650, height = 650, title = gene_value,
            xaxis={'visible': False, 'showticklabels': False},
            yaxis={'visible': False, 'showticklabels': False},
            plot_bgcolor = "white"
            )

            #fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
        cell_type_fig = px.scatter(dff, x='x',
        #x coordinates
                     y='y',
                     color = 'cell_type',
                     hover_name = 'cell_type'
                     )
        cell_type_fig.update_layout(width = 650, height = 650,
            title = 'Cell Types',
            xaxis={'visible': False, 'showticklabels': False},
            yaxis={'visible': False, 'showticklabels': False},
            plot_bgcolor = "white"
            )
        #cell_type_fig.update_xaxes(autorange=False, automargin = False)



        return gene_fig, cell_type_fig, genotype_value, df_gene_min, df_gene_max, {percentile_values[0]: '99th'}, [lower_slider_value, higher_slider_value], html.H3(analyze_cell_dict[analyze_cell_value])
        #gene_slider
    fig = px.scatter(x=[0],
                #x coordinates
                 y=[0],
                 color_discrete_sequence=['white']
                 )
    fig.update_layout(width = 650, height = 650,
        xaxis={'visible': False, 'showticklabels': False},
        yaxis={'visible': False, 'showticklabels': False},
        #paper_bgcolor = "rgba(0,0,0,0)"
        plot_bgcolor = "white",
        hovermode = False
        )
    default_slider_marks = {'10': '50th (10)'}
    #default_slider = dcc.RangeSlider(min=0, max=20, marks = None, value=[0, 20], allowCross = False, vertical = True, verticalHeight = 475)
    return fig, fig, None, 0, 20, default_slider_marks, [min(umap_graphic_gene_slider), max(umap_graphic_gene_slider)], html.H3(analyze_cell_dict[analyze_cell_value])
    #default_slider


if __name__ == '__main__':
    app.run_server(debug=True)

