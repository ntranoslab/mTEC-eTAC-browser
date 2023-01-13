import base64
import io

from dash import Dash, dcc, html, callback, Input, Output, State, ctx
import dash
import plotly.express as px
import numpy as np

import pandas as pd

dash.register_page(__name__)

##=========================Global variables=========================##
#Nolan's computer
#df = pd.read_csv('../test-data/WT_KO_thymus_subset.csv', index_col=0)
#default_gene = 'Gm26798'

df_path = '../test-data/thymus_single_cell_dec_2022.hdf5'
#df = pd.read_hdf('../test-data/thymus_single_cell_dec_2022.hdf5', index_col=0).copy(deep=False)
default_gene='Aire'
#For Lab computer
#df = pd.read_hdf('data/thymus_single_cell_dec_2022.hdf5', index_col=0)
#default_gene = 'Aire'
cell_cols_no_genes = ['cell_type', 'genotype' ,'x', 'y']
df_genes = pd.read_hdf(df_path, index_col = 0, nrows = 1).copy(deep=False)
df = pd.read_hdf(df_path, usecols = cell_cols_no_genes + [default_gene]).copy(deep=False)
genotype_list = np.insert(df['genotype'].unique(), 0, 'All')
#generate gene list
gene_list = list(df_genes.columns.unique())
#remove non-gene columns from gene list
#for i in cell_cols_no_genes:
#    gene_list.pop()
#make gene list into array
gene_list = np.array(gene_list)
colorscales = px.colors.named_colorscales()

##=========================Page Layout=========================##
layout = html.Div([
    html.Div([
        html.Div([
            html.A(
                html.Img(src='assets/gardner-lab-logo-200w-transparent.png', id = 'lab-logo'),
                href = 'https://diabetes.ucsf.edu/lab/gardner-lab',
                target = '_blank'
                ),
            ], id = 'lab-logo-link'),
            html.H3('mTECs', id = 'headline'),
            html.Div([
                    html.A(
                    html.Button('Home', className='page-buttons'),
                    href='/'
                    ),
                    html.A(
                    html.Button('mTECs', className='selected-button'),
                    href='/mtecs'
                    ),
                    html.A(
                    html.Button('eTACs', className='page-buttons'),
                    href='/etacs'
                    ),
                ], id = 'tabs'),
    ], className = 'header'),

    html.Div([
        #html.H3('UMAPs', id='graph-name-value'),
        html.Div([
            dcc.Graph(figure = px.scatter(x = [0], y=[0], color_discrete_sequence=['white']).update_layout(
                xaxis={'visible': False, 'showticklabels': False},
                yaxis={'visible': False, 'showticklabels': False},
                plot_bgcolor = "white",
                width=650, height=650),
                id='umap-graphic-gene-mtecs')
        ], style={'width': '37.5%', 'display': 'inline-block', 'marginLeft': '2%', 'marginRight': '1%'}),
        html.Div([
            dcc.Graph(figure = px.scatter(x = [0], y=[0], color_discrete_sequence=['white']).update_layout(
                xaxis={'visible': False, 'showticklabels': False},
                yaxis={'visible': False, 'showticklabels': False},
                plot_bgcolor = "white",
                width=650, height=650),
                id='umap-graphic-cell-types-mtecs')
            ], style={'width': '37.5%', 'display': 'inline-block', 'marginRight': '1%'}),
        html.Div([
            #input for gene
            html.H3('Gene:', id='gene-headline'),
            dcc.Input(placeholder = 'Select a gene...', debounce = True, id='gene-value-mtecs'),
            #dropdown for genotype
            html.H3('Genotype:', id='genotype-headline'),
            dcc.Dropdown(genotype_list, placeholder = 'Select a genotype...', id='genotype-value-mtecs'),
            #dropdown for colorscale
            html.H3('Color Scale:', id = 'color-scale-headline'),
            dcc.Dropdown(
                id= 'color-scale-dropdown',
                options = colorscales,
                value = 'plasma'
                ),
            html.H3('Color Map:', id = 'slider-headline'),
            html.Div([
                dcc.RangeSlider(min=0, max=100, allowCross = False, vertical = False, tooltip={'placement': 'top', 'always_visible': True}, id='umap-graphic-gene-slider-mtecs'),
                ], style = {'marginLeft': '5px'}),
            html.H3('Percentiles:'),
            html.Div([
                html.Button('1st', id = 'first-percentile-button'),
                html.Button('99th', id = 'ninty-ninth-percentile-button')
                ], style = {'display': 'flex', 'justify-content': 'space-between'})
        ], style={'width': '11%', 'display': 'inline-block', 'float': 'right', 'marginRight': '3.5%'}),
    ], className = 'page-body', style = {'marginLeft': '-2.75%', 'marginRight': '-2.75%'}),

    html.Div([
        html.H3('Description:', id='description-headline'),
        html.H5('About us and Links to Publications...To be, or not to be: that is the question: Whether tis nobler in the mind to suffer\\The slings and arrows of outrageous fortune,\\Or to take arms against a sea of troubles,\\And by opposing end them?\\To die: to sleep;\\No more; and by a sleep to say we end The heart-ache and the thousand natural shocksThat flesh is heir to, tis a consummation Devoutly to be wishd. // To die, to sleep;To sleep: perchance to dream: ay, theres the rub For in that sleep of death what dreams may come When we have shuffled off this mortal coil,Must give us pause: // theres the respect That makes calamity of so long life;')
        ])
    

])

    
##=========================Callback=========================##

@callback(
    Output('umap-graphic-gene-mtecs', 'figure'),
    Output('umap-graphic-cell-types-mtecs', 'figure'),
    Output('gene-value-mtecs', 'value'),
    Output('genotype-value-mtecs', 'value'),
    Output('umap-graphic-gene-slider-mtecs', 'min'),
    Output('umap-graphic-gene-slider-mtecs', 'max'),
    Output('umap-graphic-gene-slider-mtecs', 'marks'),
    Output('umap-graphic-gene-slider-mtecs', 'value'),
    Input('genotype-value-mtecs', 'value'),
    Input('gene-value-mtecs', 'value'),
    Input('umap-graphic-gene-slider-mtecs', 'value'),
    Input('color-scale-dropdown', 'value'),
    Input('first-percentile-button', 'n_clicks'),
    Input('ninty-ninth-percentile-button', 'n_clicks')
    )

def update_graph(genotype_value, gene_value, umap_graphic_gene_slider, color_scale_dropdown_value, first_per_button_click, ninty_ninth_per_button_click):

    input_id = ctx.triggered_id
    global df
    if df is not None:
        if gene_value is None:
            gene_value = default_gene
        #check if gene value is in dataframe
        gene_value_in_df = gene_value in list(df)
        #set gene value to be equal to default gene if gene not in dataframe (assuming default gene is in dataframe)
        if not gene_value_in_df:
            gene_value = default_gene
        new_columns = [gene_value] + cell_cols_no_genes
        dff = pd.read_hdf(df_path, usecols = new_columns).copy(deep=False)
        #set default genotype value to WT
        if genotype_value is None:
            genotype_value = 'WT'
        #filter df to only contain data with chosen genotype
        dff = dff[dff['genotype'] == genotype_value].copy(deep=False) if genotype_value != 'All' else dff
        #set initial gene value to be equal to default gene

        #percentile slider code
        percentile_values = np.quantile(dff[gene_value], [0.99, 0.01])
        df_gene_min = min(dff[gene_value])
        df_gene_max = max(dff[gene_value])
        if input_id == 'umap-graphic-gene-slider-mtecs':
            lower_slider_value = min(umap_graphic_gene_slider)
            higher_slider_value = max(umap_graphic_gene_slider)
        elif input_id == 'first-percentile-button':
            lower_slider_value = percentile_values[1]
            higher_slider_value = max(umap_graphic_gene_slider)
        elif input_id == 'ninty-ninth-percentile-button':
            lower_slider_value = min(umap_graphic_gene_slider)
            higher_slider_value = percentile_values[0]
        else:
            lower_slider_value = percentile_values[1]
            higher_slider_value = percentile_values[0]


        
        #graphs
        #sort dff based on cells highest expressing to lowest expressing gene - makes the gene scatter plot graph highest expressing cells on top of lower expressing cells
        gene_fig = px.scatter(dff.sort_values(by=[gene_value], kind='mergesort'),
                     #x coordinates
                     x='x',
                     #y coordinates
                     y='y',
                     color = gene_value if gene_value != None else default_gene,
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
            coloraxis_colorbar= {'thicknessmode': 'pixels', 'thickness': 30},
            xaxis={'visible': False, 'showticklabels': False},
            yaxis={'visible': False, 'showticklabels': False},
            margin={'l': 10, 'r': 10},
            plot_bgcolor = "white"
            )

        cell_type_fig = px.scatter(dff.sort_values(by=['cell_type'], kind='mergesort', ascending=False), x='x',
        #x coordinates
                     y='y',
                     color = 'cell_type',
                     color_discrete_sequence = px.colors.qualitative.Light24,
                     hover_name = 'cell_type',
                     labels={'cell_type': ''}
                     )
        cell_type_fig.update_layout(
            #width = 650, height = 650,
            autosize = True,
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
            legend={'entrywidthmode': 'pixels', 'entrywidth': 30, 'traceorder': 'reversed'},
            margin={'l':10, 'r': 10},
            xaxis={'visible': False, 'showticklabels': False},
            yaxis={'visible': False, 'showticklabels': False},
            plot_bgcolor = "white"
            )
        percentile_marks = {percentile_values[0]: '99th', percentile_values[1]: '1st'}



        return gene_fig, cell_type_fig, gene_value if gene_value_in_df else 'No Genes Found', genotype_value, df_gene_min, df_gene_max, percentile_marks, [lower_slider_value, higher_slider_value]
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

