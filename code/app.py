# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


import base64
import io

from dash import Dash, dcc, html, Input, Output, State, ctx
import plotly.express as px
import numpy as np

import pandas as pd

app = Dash(__name__)

df = None
#For Lab computer
#existing_csv = {'mTECs': pd.read_csv('../data/combined_thymus.csv', index_col=0),'eTACs': pd.read_csv('../data/combined_ln.csv', index_col=0)}
#existing_csv = {'mTECs': '../data/combined_thymus.csv','eTACs': '../data/combined_ln.csv'}
#For Nolan's computer
existing_csv = {'mTECs': '../test-data/WT_KO_thymus_subset.csv','eTACs': '../test-data/WT_KO_thymus_subset_random_genes.csv'}
#existing_csv = {'mTECs': pd.read_csv('../test-data/WT_KO_thymus_subset.csv', index_col=0),'eTACs': pd.read_csv('../test-data/WT_KO_thymus_subset_random_genes.csv', index_col=0)}
uploaded_csv = {}
cell_meta_cols = ['genotype']
cell_cols_no_genes = ['cell_type', 'genotype' ,'x', 'y']
analyze_cell_dict = {'mTECs': 'UMAPs', 'eTACs': 'tSNEs', 'Other': '', '': ''}
colorscales = px.colors.named_colorscales()
app.layout = html.Div([
    html.Div([
        html.Div([
            html.A(
                html.Img(src='assets/gardner-lab-logo-200w.png', style={'display': 'inline-block'}),
                href = 'https://diabetes.ucsf.edu/lab/gardner-lab',
                target = '_blank'
                ),
            html.H3('Analyze:', id = 'headline'),
            html.Div([
                dcc.Tabs(id='analyze-tabs', value='eTACs', children=[

            
                dcc.Tab(label='mTECs', value='mTECs'),
                dcc.Tab(label='eTACs', value='eTACs'),
                dcc.Tab(label='Other', value='Other')])
                ], style = {'float': 'right'}),
        ]),
        html.Div([
            html.H3('File:'),
            dcc.Dropdown(list(existing_csv.keys()), placeholder = 'Select a file...', id='file-value', style = {'width': '32vw'}),
            html.Div([
            dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '32vw',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                'display': 'none'
            },
            # Not allow multiple files to be uploaded
            multiple=False
            ),
        ]),
            html.Div(id = 'output-data-result', style={'float': 'right', 'display': 'none'})
        ], style={'display': 'none'}, id='file-dropdown'),
            #upload data bar
        ]),
    html.Div([
        html.H3('Category:'),
        dcc.RadioItems(cell_meta_cols, cell_meta_cols[0], id='category-value'),
        ], id = 'category'),

    html.Br(),

    html.Div([
        #dropdown with gene
        html.Div([
            html.H3('Gene:', id='gene-headline'),
            dcc.Dropdown([], placeholder = 'Select a gene...', id='gene-value')
        ], style={'width': '48%', 'display': 'inline-block'}),
        #dropdown with genotype
        html.Div([
            html.H3('Genotype:', id='genotype-headline'),
            dcc.Dropdown([], placeholder = 'Select a genotype...', id='genotype-value')
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    html.Div([
        html.H3('UMAPs', id='graph-name-value'),
        html.Div([
            dcc.Graph(figure = px.scatter(x = [0], y=[0], color_discrete_sequence=['white']).update_layout(
                xaxis={'visible': False, 'showticklabels': False},
                yaxis={'visible': False, 'showticklabels': False},
                plot_bgcolor = "white",
                width=650, height=650),
                id='umap-graphic-gene')
        ], style={'width': '45vw', 'display': 'inline-block'}),
        html.Div([
            dcc.RangeSlider(min=0, max=100, allowCross = False, vertical = True, verticalHeight = 475, tooltip={'placement': 'right', 'always_visible': True}, id='umap-graphic-gene-slider')
            ], style={'marginBottom': '60px',
                    'marginLeft': '20px',
                    'display': 'inline-block'}),
        html.Div([
            dcc.Graph(figure = px.scatter(x = [0], y=[0], color_discrete_sequence=['white']).update_layout(
                xaxis={'visible': False, 'showticklabels': False},
                yaxis={'visible': False, 'showticklabels': False},
                plot_bgcolor = "white",
                width=650, height=650),
                id='umap-graphic-cell-types')
            ], style={'width': '45vw', 'float': 'right', 'display': 'inline-block'}),
    ]),
    html.Div([
        html.P("Color Scale"),
        dcc.Dropdown(
            id= 'color-scale-dropdown',
            options = colorscales,
            value = 'plasma'
            )
        ], style = {'width': '48%'})
    

])



def check_file(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # User uploaded a CSV file
            global df
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), index_col = 0)
            if filename not in list(uploaded_csv.keys()):
                uploaded_csv[filename] = df
    except Exception as e:
        print(e)
        return html.Div([
            html.H5(filename),
            html.H5('File is not a csv.')
        ])

    return html.Div([
        html.H5(filename),

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
    Output('file-value', 'options'),
    Output('file-value', 'value'),
    Output('genotype-value', 'options'),
    Output('gene-value', 'options'),
    Output('graph-name-value', 'children'),
    Output('file-dropdown', 'style'),
    Output('upload-data', 'style'),
    Output('output-data-result', 'style'),

    Input('analyze-tabs','value'),
    #Input('analyze-cell-value', 'value'),
    Input('file-value', 'value'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
    )
def update_file(analyze_tabs, file_value, upload_data, filename):

    input_id = ctx.triggered_id
    global df
    df_path = ''
    df_no_genes = None
    df_genes = None
    file_dropdown_style={'display': 'none'}
    upload_data_style={'display': 'none'}
    output_data_result_style={'display': 'none'}
    if input_id is None:
        if analyze_tabs != 'Other':
            df_path = existing_csv.get(analyze_tabs, 'No such file exists')
        else:
            return html.Div([
                'No File Uploaded'
                ]), list(uploaded_csv.keys()), '', [], [], html.H3(analyze_cell_dict[analyze_tabs]), file_dropdown_style, upload_data_style, output_data_result_style
    if analyze_tabs == 'Other':
        file_dropdown_style={'width': '32vw', 'display': 'inline-block'}
        upload_data_style={
            'width': '30vw',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'display': 'inline-block'
            }
        output_data_result_style={'display': 'inline-block'}
    if input_id == 'analyze-tabs':
        if analyze_tabs == 'Other':
            file_dropdown_style={'width': '32vw', 'display': 'inline-block'}
            upload_data_style={
                'width': '30vw',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                'display': 'inline-block'
            }
            output_data_result_style={'display': 'inline-block'}
            if file_value is None or file_value=='':
                return html.Div([
            'No File Uploaded'
        ]), list(uploaded_csv.keys()), '', [], [], html.H3(analyze_cell_dict[analyze_tabs]), file_dropdown_style, upload_data_style, output_data_result_style
            else:
                df = uploaded_csv.get(file_value, 'No such file exists')
        else:
            df_path = existing_csv.get(analyze_tabs, 'No such file exists')
            df_no_genes = pd.read_csv(df_path, usecols = cell_cols_no_genes)
            df_genes = pd.read_csv(df_path, nrows = 1)
            df = pd.read_csv(df_path, usecols = cell_cols_no_genes + [df_genes.columns[0]])
    elif input_id == 'file-value':
        df = uploaded_csv.get(file_value, 'No such file exists')
    elif input_id == 'upload-data':
        #is upload_data in correct format? is upload_data a csv? assign df to csv
        check_file(upload_data, filename)
        file_value = filename
    #generate genotype list
    if df_path == '':
        genotype_list = np.insert(df['genotype'].unique(), 0, 'All')
        #generate gene list
        gene_list = list(df.columns.unique())
        #remove cell_type col from gene list
        gene_list.remove('cell_type')
        #remove genotype col from gene list
        gene_list.remove('genotype')
        #remove x col from gene list
        gene_list.remove('x')
        #remove y col from gene list
        gene_list.remove('y')
        #make gene list into array
        gene_list = np.array(gene_list)
    else:
        df_no_genes = pd.read_csv(df_path, usecols = cell_cols_no_genes)
        df_genes = pd.read_csv(df_path, index_col = 0, nrows = 1)
        df = pd.read_csv(df_path, usecols = cell_cols_no_genes + [df_genes.columns[0]])
        genotype_list = np.insert(df_no_genes['genotype'].unique(), 0, 'All')
        #generate gene list
        gene_list = list(df_genes.columns.unique())
        #remove cell_type col from gene list
        gene_list.remove('cell_type')
        #remove genotype col from gene list
        gene_list.remove('genotype')
        #remove x col from gene list
        gene_list.remove('x')
        #remove y col from gene list
        gene_list.remove('y')
        #make gene list into array
        gene_list = np.array(gene_list)

    return html.Div([
        html.H5(file_value),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        #html.Div('Raw Content'),
        #html.Pre(contents[0:200] + '...', style={
        #    'whiteSpace': 'pre-wrap',
        #    'wordBreak': 'break-all'
        #})
    ]), list(uploaded_csv.keys()), file_value, genotype_list, gene_list, html.H3(analyze_cell_dict[analyze_tabs]), file_dropdown_style, upload_data_style, output_data_result_style
    

@app.callback(
    Output('umap-graphic-gene', 'figure'),
    Output('umap-graphic-cell-types', 'figure'),
    Output('gene-value', 'value'),
    Output('genotype-value', 'value'),
    Output('umap-graphic-gene-slider', 'min'),
    Output('umap-graphic-gene-slider', 'max'),
    Output('umap-graphic-gene-slider', 'marks'),
    Output('umap-graphic-gene-slider', 'value'),
    Input('genotype-value', 'value'),
    Input('gene-value', 'value'),
    Input('umap-graphic-gene-slider', 'value'),
    Input('color-scale-dropdown', 'value'),
    Input('analyze-tabs', 'value')
    )
def update_graph(genotype_value, gene_value, umap_graphic_gene_slider, color_scale_dropdown_value, analyze_tabs):

    input_id = ctx.triggered_id
    df_path = existing_csv.get(analyze_tabs, 'No such file exists')
    global df
    if df is not None:

        #filter df to only contain data with chosen genotype
        if genotype_value is None:
            genotype_value = 'All'
        if analyze_tabs != 'Other':
            df_genes = pd.read_csv(df_path, index_col = 0, nrows = 1)
            df = pd.read_csv(df_path, usecols = cell_cols_no_genes + [gene_value]) if (gene_value != None and gene_value in list(df_genes)) else pd.read_csv(df_path, usecols = cell_cols_no_genes + [df_genes.columns[0]])

        dff = df[df['genotype'] == genotype_value] if genotype_value != 'All' else df
        if gene_value is None or gene_value not in list(dff):
            first_gene = list(dff)[0]
            #make sure there is actually at least one gene in the csv
            if first_gene is not None and first_gene != 'cell_type' and first_gene != 'genotype' and first_gene != 'x' and first_gene != 'y':
                gene_value = first_gene
            else:
                print('no genes found')
        #dff = dff[[gene_value, 'cell_type', 'genotype', 'x', 'y']] if gene_value != None else dff
        percentile_values = np.quantile(dff[gene_value], [0.99, 0.01])
        df_gene_min = min(dff[gene_value])
        df_gene_max = max(dff[gene_value])
        lower_slider_value = percentile_values[1] if input_id != 'umap-graphic-gene-slider' else min(umap_graphic_gene_slider)
        higher_slider_value = percentile_values[0] if input_id != 'umap-graphic-gene-slider' else max(umap_graphic_gene_slider)

        gene_fig = px.scatter(dff,
                     #x coordinates
                     x='x',
                     #y coordinates
                     y='y',
                     color = gene_value,
                     hover_name = 'cell_type',
                     range_color=
                     #min of color range
                     [lower_slider_value, 
                     #max of color range
                     higher_slider_value],
                     color_continuous_scale = color_scale_dropdown_value
                     )
        gene_fig.update_layout(
            autosize = True,
            minreducedwidth=650,
            minreducedheight=650,
            title = gene_value,
            xaxis={'visible': False, 'showticklabels': False},
            yaxis={'visible': False, 'showticklabels': False},
            plot_bgcolor = "white"
            )

        cell_type_fig = px.scatter(dff, x='x',
        #x coordinates
                     y='y',
                     color = 'cell_type',
                     hover_name = 'cell_type',
                     )
        cell_type_fig.update_layout(
            #width = 650, height = 650,
            autosize = True,
            minreducedwidth=650,
            minreducedheight=650,
            title = 'Cell Types',
            xaxis={'visible': False, 'showticklabels': False},
            yaxis={'visible': False, 'showticklabels': False},
            plot_bgcolor = "white"
            )
        percentile_marks = {percentile_values[0]: '99th', percentile_values[1]: '1st'}



        return gene_fig, cell_type_fig, gene_value, genotype_value, df_gene_min, df_gene_max, percentile_marks, [lower_slider_value, higher_slider_value]
        #gene_slider
    fig = px.scatter(x=[0],
                 y=[0],
                 color_discrete_sequence=['white']
                 )
    fig.update_layout(
        width = 650, height = 650,
        xaxis={'visible': False, 'showticklabels': False},
        yaxis={'visible': False, 'showticklabels': False},
        margin = dict(l=50, r=50, t=50, b=50, pad=4),
        plot_bgcolor = "white",
        hovermode = False
        )
    default_percentiles = np.quantile([0, 100], [0.99, 0.01])
    default_slider_marks = {int(default_percentiles[0]): '99th', int(default_percentiles[1]): '1st'}
    return fig, fig, None, None, 0, 100, default_slider_marks, [default_percentiles[1], default_percentiles[0]]


if __name__ == '__main__':
    app.run_server(debug=True)

