import base64
import io

from dash import Dash, dcc, html, callback, Input, Output, State, ctx
import dash
import plotly.express as px
import numpy as np
import sqlalchemy as db

import pandas as pd
import csv
import os
import boto3
import sys

dash.register_page(__name__)

##=========================Global variables=========================##
database = 'thymus'
if ('LOCALDEV' in os.environ) | ('LOCALDEPLOY' in os.environ):
    host = 'localhost'
    user = 'root'
    passwd = os.environ.get('MYSQLPASSWORD')
else:
    ssm = boto3.client('ssm', region_name='us-west-2')
    host = ssm.get_parameter(Name= "RDS_HOSTNAME")['Parameter']['Value']
    user = ssm.get_parameter(Name= "RDS_USERNAME")['Parameter']['Value']
    passwd = ssm.get_parameter(Name= "RDS_PASSWORD", WithDecryption = True)['Parameter']['Value']


engine = db.create_engine(f"mysql+pymysql://{user}:{passwd}@{host}/{database}")

default_gene='aire'

metadata = pd.read_sql('cellmetadata', con=engine)
with open(f"static/{database}_gene_table_lookup.csv") as f:
    next(f)  # Skip the header
    reader = csv.reader(f, skipinitialspace=True)
    gene_lookup = dict(reader)
gene_list = gene_lookup.keys()
genotype_list = np.insert(metadata.genotype.unique(), 0, 'All')

colorscales = ['bluered', 'blues', 'cividis', 'dense', 'hot', 'ice', 'inferno', 'magenta', 'magma', 'picnic', 'plasma', 'plotly3', 'purp', 'purples', 'rdpu', 'rdylbu', 'teal', 'viridis']

##=========================Page Layout=========================##
layout = html.Div([
    html.Div([
        html.Div([
            html.A(
                html.Img(src='static/gardner-lab-logo-200w-transparent.png', id = 'lab-logo'),
                href = 'https://diabetes.ucsf.edu/lab/gardner-lab',
                target = '_blank'
                ),
            ], id = 'lab-logo-link'),
            html.H3('Thymus', id = 'headline'),
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

    html.Br(),

    html.Div([
        html.Div([
            html.Br(),
            html.H1('Data Browser', className='graph-titles',style={'marginLeft': '2.5%', 'color': '#3F6CB4'}),
            html.Div([
                #input for gene
                html.H3('Gene:', id='gene-headline'),
                dcc.Input(placeholder = 'Select a gene...', debounce = True, id='gene-value-mtecs'),
                #dropdown for genotype
                html.H3('Genotype:', id='genotype-headline'),
                dcc.Dropdown(genotype_list, placeholder = 'Select a genotype...', id='genotype-value-mtecs'),
                #dropdown for colorscale
                html.H3('Color Map:', id = 'color-scale-headline'),
                dcc.Dropdown(
                    id= 'color-scale-dropdown',
                    options = colorscales,
                    value = 'plasma'
                    ),
                html.H4('Scale', id = 'slider-headline'),
                html.Div([
                    dcc.RangeSlider(min=0, max=100, allowCross = False, vertical = False, tooltip={'placement': 'top', 'always_visible': True}, id='umap-graphic-gene-slider-mtecs'),
                    ], style = {'marginLeft': '5px'}),
                html.H4('Percentiles', id = 'percentile-headline'),
                html.Div([
                    html.Button('1st', id = 'first-percentile-button'),
                    html.Button('99th', id = 'ninty-ninth-percentile-button')
                    ], style = {'display': 'flex', 'justify-content': 'space-between'})
            ], style={'width': '11%', 'display': 'inline-block', 'float': 'right', 'marginRight': '3.5%'}),
            html.Div([
                dcc.Loading([
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
                ], color='#3F6CB4', type='cube', style={'marginRight': '10%', 'display': 'flex'}),
            ]),
        ]),
        html.Div([
            html.Br(),
            html.H1('Genotype Comparison', className='graph-titles',style={'marginLeft': '2.5%', 'color': '#3F6CB4'}),
            html.Br(),
            html.Div([
                #input for gene
                html.H3('Gene:', id='gene-headline'),
                dcc.Input(placeholder = 'Select a gene...', debounce = True, id='genotype-graph-gene-value'),
                #dropdown for colorscale
                html.H3('Color Map:', id = 'color-scale-headline'),
                dcc.Dropdown(
                    id= 'color-scale-dropdown-genotype',
                    options = colorscales,
                    value = 'plasma'
                    ),
                html.H4('Scale', id = 'slider-headline'),
                html.Div([
                    dcc.RangeSlider(min=0, max=100, allowCross = False, vertical = False, tooltip={'placement': 'top', 'always_visible': True}, id='genotype-graph-gene-slider'),
                    ], style = {'marginLeft': '5px'}),
                html.H4('Percentiles (from left graph genotype)', id = 'percentile-headline'),
                html.Div([
                    html.Button('1st', id = 'first-percentile-button-genotype'),
                    html.Button('99th', id = 'ninty-ninth-percentile-button-genotype')
                    ], style = {'display': 'flex', 'justify-content': 'space-between'})
            ], style={'width': '11%', 'display': 'inline-block', 'float': 'right', 'marginRight': '3.5%'}),
            html.Div([
                html.Div([
                    dcc.Dropdown(genotype_list, placeholder = 'Select a genotype...', id='genotype-value-left'),
                    dcc.Loading([
                        dcc.Graph(figure = px.scatter(x = [0], y=[0], color_discrete_sequence=['white']).update_layout(
                            xaxis={'visible': False, 'showticklabels': False},
                            yaxis={'visible': False, 'showticklabels': False},
                            plot_bgcolor = "white",
                            width=650, height=650),
                            id='genotype-graph-left')
                    ], color='#3F6CB4', type='cube', style={'marginRight': '10%', 'display': 'flex'}),
                ], style={'width': '37.5%', 'marginRight': '1%'}),
                html.Button('Swap', id='genotype-swap-button'),
                html.Div([
                    dcc.Dropdown(genotype_list, placeholder = 'Select a genotype...', id='genotype-value-right'),
                    dcc.Loading([
                        dcc.Graph(figure = px.scatter(x = [0], y=[0], color_discrete_sequence=['white']).update_layout(
                            xaxis={'visible': False, 'showticklabels': False},
                            yaxis={'visible': False, 'showticklabels': False},
                            plot_bgcolor = "white",
                            width=650, height=650),
                            id='genotype-graph-right')

                    ], color='#3F6CB4', type='cube', style={'marginRight': '10%', 'display': 'flex'}),
                ], style={'width': '37.5%', 'marginLeft': '1%'}),
            ], style = {'display': 'flex', 'justify-content': 'center'}),
        ]),
    ], className = 'page-body', style = {'marginLeft': '-2.75%', 'marginRight': '-2.75%'}),

    html.Div([
        html.H3('Description:', id='description-headline'),
        html.H5('About us and Links to Publications...To be, or not to be: that is the question: Whether tis nobler in the mind to suffer\\The slings and arrows of outrageous fortune,\\Or to take arms against a sea of troubles,\\And by opposing end them?\\To die: to sleep;\\No more; and by a sleep to say we end The heart-ache and the thousand natural shocksThat flesh is heir to, tis a consummation Devoutly to be wishd. // To die, to sleep;To sleep: perchance to dream: ay, theres the rub For in that sleep of death what dreams may come When we have shuffled off this mortal coil,Must give us pause: // theres the respect That makes calamity of so long life;', id = 'description')
        ])
    

])

    
##=========================Callbacks=========================##
#First row of graphs (data browser)

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
    global metadata
    if metadata is not None:
        if gene_value is None:
            gene_value = default_gene
        #first lower case gene value
        gene_value = gene_value.lower()

        #check if gene value is in dataframe
        gene_value_in_df = gene_value in gene_list
        #set gene value to be equal to default gene if gene not in dataframe (assuming default gene is in dataframe)
        if not gene_value_in_df:
            gene_value = default_gene

        #table to get gene_value from
        table = gene_lookup[gene_value]
        #extract gene column from table
        gene_data = pd.read_sql(table, con=engine, columns = [gene_value, 'barcode'])
        #set default genotype value to WT
        if genotype_value is None:
            genotype_value = 'WT'
        #makes genotype value into list of selected genotypes
        if genotype_value != 'All':
            metadata_subset = metadata[metadata.genotype == genotype_value]
        else:
            metadata_subset = metadata

        #subset expression data on selected cells [gene_value, meta_cols]
        gene_data = pd.merge(gene_data, metadata_subset, on='barcode', how='inner')
        #set initial gene value to be equal to default gene

        #percentile slider code
        percentile_values = np.quantile(gene_data[gene_value], [0.99, 0.01])
        df_gene_min = min(gene_data[gene_value])
        df_gene_max = max(gene_data[gene_value])
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
        gene_fig = px.scatter(gene_data.sort_values(by=[gene_value], kind='mergesort'),
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

        cell_type_fig = px.scatter(gene_data.sort_values(by=['cell_type'], kind='mergesort', ascending=False), x='x',
        #x coordinates
                     y='y',
                     color = 'cell_type',
                     color_discrete_sequence = px.colors.qualitative.Light24,
                     hover_name = 'cell_type',
                     labels={'cell_type': ''}
                     )
        cell_type_fig.update_layout(
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


##=========================Callback=========================##
#Second row of graphs (genotype comparison)

@callback(
    Output('genotype-graph-left', 'figure'),
    Output('genotype-graph-right', 'figure'),
    Output('genotype-value-left', 'value'),
    Output('genotype-value-right', 'value'),
    Output('genotype-graph-gene-value', 'value'),
    Output('genotype-graph-gene-slider', 'min'),
    Output('genotype-graph-gene-slider', 'max'),
    Output('genotype-graph-gene-slider', 'marks'),
    Output('genotype-graph-gene-slider', 'value'),
    Input('genotype-value-left', 'value'),
    Input('genotype-value-right', 'value'),
    Input('genotype-graph-gene-value', 'value'),
    Input('genotype-graph-gene-slider', 'value'),
    Input('color-scale-dropdown-genotype', 'value'),
    Input('first-percentile-button-genotype', 'n_clicks'),
    Input('ninty-ninth-percentile-button-genotype', 'n_clicks'),
    Input('genotype-swap-button', 'n_clicks')
    )

def update_graph(genotype_value_left, genotype_value_right, gene_value, genotype_graph_gene_slider, color_scale_dropdown_value, first_per_button_click, ninty_ninth_per_button_click, swap_button_click):

    input_id = ctx.triggered_id
    global metadata
    if metadata is not None:
        if gene_value is None:
            gene_value = default_gene
        #first lower case gene value
        gene_value = gene_value.lower()

        #check if gene value is in dataframe
        gene_value_in_df = gene_value in gene_list
        #set gene value to be equal to default gene if gene not in dataframe (assuming default gene is in dataframe)
        if not gene_value_in_df:
            gene_value = default_gene

        #table to get gene_value from
        table = gene_lookup[gene_value]
        #extract gene column from table
        gene_data = pd.read_sql(table, con=engine, columns = [gene_value, 'barcode'])
        #set default genotype value to WT
        genotype_value_left = 'WT' if genotype_value_left is None else genotype_value_left
        genotype_value_right = 'Aire_KO' if genotype_value_right is None else genotype_value_right
        #swap genotypes between graphs
        if input_id == 'genotype-swap-button':
            genotype_value_temp = genotype_value_left
            genotype_value_left = genotype_value_right
            genotype_value_right = genotype_value_temp
        #makes genotype value into list of selected genotypes
        if genotype_value_left != 'All':
            metadata_subset_left = metadata[metadata.genotype == genotype_value_left]
        else:
            metadata_subset_left = metadata
        if genotype_value_right != 'All':
            metadata_subset_right = metadata[metadata.genotype == genotype_value_right]
        else:
            metadata_subset_right = metadata

        #subset expression data on selected cells [gene_value, meta_cols]
        gene_data_left = pd.merge(gene_data, metadata_subset_left, on='barcode', how='inner')
        gene_data_right = pd.merge(gene_data, metadata_subset_right, on='barcode', how='inner')

        #percentile slider code
        percentile_values = np.quantile(gene_data_left[gene_value], [0.99, 0.01])
        df_gene_min = min(gene_data_left[gene_value])
        df_gene_max = max(gene_data_left[gene_value])
        if input_id == 'genotype-graph-gene-slider':
            lower_slider_value = min(genotype_graph_gene_slider)
            higher_slider_value = max(genotype_graph_gene_slider)
        elif input_id == 'first-percentile-button':
            lower_slider_value = percentile_values[1]
            higher_slider_value = max(genotype_graph_gene_slider)
        elif input_id == 'ninty-ninth-percentile-button':
            lower_slider_value = min(genotype_graph_gene_slider)
            higher_slider_value = percentile_values[0]
        else:
            lower_slider_value = percentile_values[1]
            higher_slider_value = percentile_values[0]


        
        #graphs
        #sort dff based on cells highest expressing to lowest expressing gene - makes the gene scatter plot graph highest expressing cells on top of lower expressing cells
        gene_fig_left = px.scatter(gene_data_left.sort_values(by=[gene_value], kind='mergesort'),
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
        gene_fig_left.update_layout(
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

        gene_fig_right = px.scatter(gene_data_right.sort_values(by=[gene_value], kind='mergesort'),
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
        gene_fig_right.update_layout(
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

        percentile_marks = {percentile_values[0]: '99th', percentile_values[1]: '1st'}



        return gene_fig_left, gene_fig_right, genotype_value_left, genotype_value_right, gene_value if gene_value_in_df else 'No Genes Found', df_gene_min, df_gene_max, percentile_marks, [lower_slider_value, higher_slider_value]
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
    return fig, fig, None, None, None, 0, 100, [], [], html.H3(''), default_slider_marks, [default_percentiles[1], default_percentiles[0]]

