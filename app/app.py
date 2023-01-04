# Run this app with `python app.py` and
# visit http://localhost:8050/ in your web browser.


import base64
import io

from dash import Dash, dcc, html, Input, Output, State, ctx
import plotly.express as px
import numpy as np

import pandas as pd

app = Dash(__name__)
server = app.server

##=========================Global variables=========================##
#Nolan's computer
df = pd.read_csv('../test-data/WT_KO_thymus_subset.csv', index_col=0)
#df = pd.read_csv('../thymus_single_cell_dec_2022.csv', index_col=0)
default_gene = 'Aire'
#For Lab computer
#df = pd.read_csv('data/thymus_single_cell_dec_2022.csv', index_col=0)
cell_cols_no_genes = ['cell_type', 'genotype' ,'x', 'y']
genotype_list = np.insert(df['genotype'].unique(), 0, 'All')
#generate gene list
gene_list = list(df.columns.unique())
#remove non-gene columns from gene list
for i in cell_cols_no_genes:
    gene_list.remove(i)
#make gene list into array
gene_list = np.array(gene_list)
colorscales = px.colors.named_colorscales()

##=========================Page Layout=========================##
app.layout = html.Div([
    html.Div([
        html.A(
            html.Img(src='assets/gardner-lab-logo-200w.png', style={'display': 'inline-block'}),
            href = 'https://diabetes.ucsf.edu/lab/gardner-lab',
            target = '_blank'
            ),
        html.H3('Analyze:', id = 'headline'),
        html.Div([
            dcc.Tabs(id='analyze-tabs', value='mTECs', children=[

        
            dcc.Tab(label='mTECs', value='mTECs')
            #dcc.Tab(label='eTACs', value='eTACs'),
            #dcc.Tab(label='Other', value='Other')
            ])
            ], style = {'float': 'right'}),
    ], className = 'header'),

    html.Br(),

    html.Div([
        #html.H3('UMAPs', id='graph-name-value'),
        html.Div([
            dcc.Graph(figure = px.scatter(x = [0], y=[0], color_discrete_sequence=['white']).update_layout(
                xaxis={'visible': False, 'showticklabels': False},
                yaxis={'visible': False, 'showticklabels': False},
                plot_bgcolor = "white",
                width=650, height=650),
                id='umap-graphic-gene')
        ], style={'width': '40vw', 'display': 'inline-block'}),
        html.Div([
            dcc.RangeSlider(min=0, max=100, allowCross = False, vertical = True, verticalHeight = 475, tooltip={'placement': 'right', 'always_visible': True}, id='umap-graphic-gene-slider')
            ], style={'marginBottom': '60px',
                    'marginLeft': '10px',
                    'marginRight': '20px',
                    'display': 'inline-block'}),
        html.Div([
            dcc.Graph(figure = px.scatter(x = [0], y=[0], color_discrete_sequence=['white']).update_layout(
                xaxis={'visible': False, 'showticklabels': False},
                yaxis={'visible': False, 'showticklabels': False},
                plot_bgcolor = "white",
                width=650, height=650),
                id='umap-graphic-cell-types')
            ], style={'width': '40vw', 'display': 'inline-block'}),
        html.Div([
            #input for gene
            html.H3('Gene:', id='gene-headline'),
            dcc.Input(placeholder = 'Select a gene...', debounce = True, id='gene-value'),
            #dropdown for genotype
            html.H3('Genotype:', id='genotype-headline'),
            dcc.Dropdown(genotype_list, placeholder = 'Select a genotype...', id='genotype-value'),
            #dropdown for colorscale
            html.H3('Color Scale:', id = 'color-scale-headline'),
            dcc.Dropdown(
                id= 'color-scale-dropdown',
                options = colorscales,
                value = 'plasma'
                ),
            html.Br(),
            html.Div([
                html.Button('1st'),
                html.Button('99th')
                ], style = {'display': 'inline-block'})
        ], style={'width': '8%', 'float': 'right', 'display': 'inline-block', 'marginRight': '1%'}),
    ], className = 'graphs'),
    

])

    
##=========================Callback=========================##

@app.callback(
    Output('umap-graphic-gene', 'figure'),
    Output('umap-graphic-cell-types', 'figure'),
    Output('genotype-value', 'value'),
    Output('umap-graphic-gene-slider', 'min'),
    Output('umap-graphic-gene-slider', 'max'),
    Output('umap-graphic-gene-slider', 'marks'),
    Output('umap-graphic-gene-slider', 'value'),
    Input('genotype-value', 'value'),
    Input('gene-value', 'value'),
    Input('umap-graphic-gene-slider', 'value'),
    Input('color-scale-dropdown', 'value')
    )

def update_graph(genotype_value, gene_value, umap_graphic_gene_slider, color_scale_dropdown_value):

    input_id = ctx.triggered_id
    global df
    if df is not None:
        #filter df to only contain data with chosen genotype
        if genotype_value is None:
            genotype_value = 'WT'
        dff = df[df['genotype'] == genotype_value] if genotype_value != 'All' else df
        if gene_value is None or gene_value not in list(dff):
            gene = default_gene if default_gene in list(dff) else list(dff)[0]
            #make sure there is actually at least one gene in the csv
            if gene is not None and gene not in cell_cols_no_genes:
                gene_value = gene
            else:
                print('no genes found')
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
                     color_continuous_scale = color_scale_dropdown_value,
                     labels = {gene_value: ''}
                     )
        gene_fig.update_layout(
            autosize = True,
            minreducedwidth=650,
            minreducedheight=650,
            title = {
                'text': '<b>' + gene_value + '</b>',
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {
                    'size': 20,
                    'family': 'Arial',
                    'color': '#4C5C75'
                }
            },
            xaxis={'visible': False, 'showticklabels': False},
            yaxis={'visible': False, 'showticklabels': False},
            plot_bgcolor = "white"
            )

        cell_type_fig = px.scatter(dff, x='x',
        #x coordinates
                     y='y',
                     color = 'cell_type',
                     hover_name = 'cell_type',
                     labels={'cell_type': ''}
                     )
        cell_type_fig.update_layout(
            #width = 650, height = 650,
            autosize = True,
            minreducedwidth=650,
            minreducedheight=650,
            title = {
                'text': '<b>Cell Types</b>',
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {
                    'size': 20,
                    'family': 'Arial',
                    'color': '#4C5C75'
                }
            },
            xaxis={'visible': False, 'showticklabels': False},
            yaxis={'visible': False, 'showticklabels': False},
            plot_bgcolor = "white"
            )
        percentile_marks = {percentile_values[0]: '99th', percentile_values[1]: '1st'}



        return gene_fig, cell_type_fig, genotype_value, df_gene_min, df_gene_max, percentile_marks, [lower_slider_value, higher_slider_value]
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
    return fig, fig, None, None, 0, 100, [], [], html.H3(''), default_slider_marks, [default_percentiles[1], default_percentiles[0]]

##=========================Local development only=========================##
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

