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
database = 'lymphnode'
if ('LOCALDEV' in os.environ) | ('LOCALDEPLOY' in os.environ):
    host = 'gardner-lab-computer'
    user = 'nolan'
    passwd = os.getenv('MYSQLPASSWORD')
else:
    ssm = boto3.client('ssm', region_name='us-west-2')
    host = ssm.get_parameter(Name= "RDS_HOSTNAME")['Parameter']['Value']
    user = ssm.get_parameter(Name= "RDS_USERNAME")['Parameter']['Value']
    passwd = ssm.get_parameter(Name= "RDS_PASSWORD", WithDecryption = True)['Parameter']['Value']


engine = db.create_engine(f"mysql+pymysql://{user}:{passwd}@{host}/{database}")
engine_counts = db.create_engine(f"mysql+pymysql://{user}:{passwd}@{host}/{database}_counts")

default_gene='aire'

default_expression_data_value = 'Normalized'

metadata = pd.read_sql('cellmetadata', con=engine)
with open(f"static/{database}_gene_table_lookup.csv") as f:
    next(f)  # Skip the header
    reader = csv.reader(f, skipinitialspace=True)
    gene_lookup = dict(reader)
gene_list = gene_lookup.keys()
gene_list = list(gene_list)
for i in range(len(gene_list)):
    gene_list[i] = gene_list[i].capitalize()

color_list = ['#1f77b4',
 '#aec7e8',
 '#ff7f0e',
 '#ffbb78',
 '#2ca02c',
 '#98df8a',
 '#d62728',
 '#ff9896',
 '#9467bd',
 '#c5b0d5',
 '#8c564b',
 '#c49c94',
 '#e377c2',
 '#f7b6d2',
 '#7f7f7f',
 '#bcbd22',
 '#dbdb8d',
 '#17becf',
 '#8dd3c7',
 '#bebada',
 '#fb8072',
 '#b3de69',
 '#bc80bd',
 '#ccebc5',
 '#ffed6f',
 'darkred',
 'darkblue']

sorted_cell_list = metadata.cell_type.unique().copy()
sorted_cell_list.sort()

checklist_children = [{"label": html.Div([
    html.Button(disabled = True, style={'background-color': color_list[i]}, className = 'icon-button'),
    html.Div(sorted_cell_list[i], style={'font-size': 12, 'padding-left': 10, 'color': 'black'}),
    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}), "value": sorted_cell_list[i]} for i in range(len(sorted_cell_list))]
# checklist_children.insert(0, {"label": html.Div("All", style={'font-size': 12, 'padding-left': 10, 'color': 'black'}), "value": "All"})

if len(color_list) >= len(metadata.cell_type.unique()):
    color_list = color_list[0:len(metadata.cell_type.unique())]
    color_list.reverse()
else:
    color_list.reverse()

checklist_colors = [{"label": html.Area(shape = 'circle', style={'color': 'blue', 'width': 10}), "value": sorted_cell_list[i]} for i in range(len(sorted_cell_list))]


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
            html.H3('Lymph Nodes', id = 'headline'),
            html.Div([
                    html.A(
                    html.Button('Home', className='page-buttons'),
                    href='/'
                    ),
                    html.A(
                    html.Button('mTECs', className='page-buttons'),
                    href='/mtecs'
                    ),
                    html.A(
                    html.Button('eTACs', className='selected-button'),
                    href='/etacs'
                    ),
                ], id = 'tabs'),
    ], className = 'header'),

    html.Br(),


    html.Div([
        html.Div([
            html.Button(className = 'icon-button'),
            html.Br(),
            html.H1('Data Browser', className='graph-titles',style={'marginLeft': '2.5%', 'color': '#3F6CB4'}),
            html.Div([
                #input for gene
                html.H3('Gene:', id='gene-headline'),
                dcc.Dropdown(gene_list, placeholder = 'Select a gene...', id='gene-value-etacs'),
                #dropdown for counts vs normalized
                html.H3('Expression data:', id='expression-data-headline'),
                dcc.Dropdown(['Raw counts', 'Normalized'], placeholder = 'Select a visualization...', id='expression-data-value-etacs'),
                #slideer for dot size
                html.H3('Dot size', id = 'dot-size-headline'),
                html.Div([
                    dcc.Slider(min=3, max=10, step=1, marks=None, included=False, vertical=False, tooltip={'placement': 'top', 'always_visible': True}, id='dot-size-slider-data-browser-etacs'),
                    ], style = {'marginLeft': '-12%','width': '122%'}),
            ], style={'width': '11%', 'display': 'inline-block', 'float': 'right', 'marginRight': '3.5%'}),
            dcc.Loading([
                    html.Div([
                        html.Div([
                            dcc.Graph(figure = px.scatter(x = [0], y=[0], color_discrete_sequence=['white']).update_layout(
                                xaxis={'visible': False, 'showticklabels': False},
                                yaxis={'visible': False, 'showticklabels': False},
                                plot_bgcolor = "white",
                                width=650, height=650),
                                id='umap-graphic-gene-etacs')
                        ], style={'width': '45%', 'marginRight': '1.5%'}),
                        html.Div([
                            dcc.Graph(figure = px.scatter(x = [0], y=[0], color_discrete_sequence=['white']).update_layout(
                                xaxis={'visible': False, 'showticklabels': False},
                                yaxis={'visible': False, 'showticklabels': False},
                                plot_bgcolor = "white",
                                width=650, height=650),
                                id='umap-graphic-cell-types-etacs')
                        ], style={'width': '37%', 'marginLeft': '1.5%'}),
                        html.Div([
                            dcc.Checklist(["All"], ["All"], labelStyle = {'display': 'flex'}, style={'padding-top': '3%', 'padding-right': '2%', 'font-size': 12, 'color': 'black'}, id="all-cell-type-checklist"),
                            dcc.Checklist(checklist_children, sorted_cell_list[0:len(sorted_cell_list)], labelStyle = {'display': 'flex'}, style={'padding-right': '2%'}, id='cell-type-checklist'),
                        ]),
                    ], style = {'display': 'flex', 'justify-content': 'center'}),
                ], color='#3F6CB4', type='cube', style={'marginRight': '10%'}),

                #sorted_cell_list[0:len(sorted_cell_list)]),
        ]),
        html.Div([
            html.Div([
                html.H3('Color Map:', id = 'color-scale-headline', style = {'text-align': 'center'}),
                dcc.Dropdown(
                    id= 'color-scale-dropdown',
                    options = colorscales,
                    value = 'plasma'
                ),
            ], style = {'width': '27.5%'}),
            html.Div([
                html.H4('Scale', id = 'slider-headline'),
                html.Div([
                    dcc.RangeSlider(min=0, max=100, allowCross = False, vertical = False, tooltip={'placement': 'top', 'always_visible': True}, id='umap-graphic-gene-slider-etacs'),
                ], style = {'marginLeft': '5px'}),
            ], style = {'width': '27.5%'}),
            html.Div([
                html.H4('Percentiles', id = 'percentile-headline'),
                    html.Div([
                        html.Button('1st', id = 'first-percentile-button'),
                        html.Button('99th', id = 'ninty-ninth-percentile-button')
                    ], style = {'display': 'flex', 'justify-content': 'space-between'})
            ], style = {'width': '27.5%', 'marginBottom': '10%'}),
        ], style={'marginLeft': '2.5%','display': 'flex', 'justify-content': 'space-evenly', 'width': '35%'}),

    ], className = 'page-body', style = {'marginLeft': '-2.75%', 'marginRight': '-2.75%'}),

    html.Div([
        html.H3('Description:', id='description-headline'),
        html.H5('About us and Links to Publications...To be, or not to be: that is the question: Whether tis nobler in the mind to suffer\\The slings and arrows of outrageous fortune,\\Or to take arms against a sea of troubles,\\And by opposing end them?\\To die: to sleep;\\No more; and by a sleep to say we end The heart-ache and the thousand natural shocksThat flesh is heir to, tis a consummation Devoutly to be wishd. // To die, to sleep;To sleep: perchance to dream: ay, theres the rub For in that sleep of death what dreams may come When we have shuffled off this mortal coil,Must give us pause: // theres the respect That makes calamity of so long life;', id = 'description')
        ])
    

])

    
##=========================Callback=========================##

@callback(
    Output('umap-graphic-gene-etacs', 'figure'),
    Output('umap-graphic-cell-types-etacs', 'figure'),
    Output('gene-value-etacs', 'value'),
    Output('expression-data-value-etacs', 'value'),
    Output('dot-size-slider-data-browser-etacs', 'value'),
    Output('umap-graphic-gene-slider-etacs', 'min'),
    Output('umap-graphic-gene-slider-etacs', 'max'),
    Output('umap-graphic-gene-slider-etacs', 'marks'),
    Output('umap-graphic-gene-slider-etacs', 'value'),
    Output('all-cell-type-checklist', 'value'),
    Output('cell-type-checklist', 'value'),
    Input('gene-value-etacs', 'value'),
    Input('expression-data-value-etacs', 'value'),
    Input('dot-size-slider-data-browser-etacs', 'value'),
    Input('umap-graphic-gene-slider-etacs', 'value'),
    Input('color-scale-dropdown', 'value'),
    Input('first-percentile-button', 'n_clicks'),
    Input('ninty-ninth-percentile-button', 'n_clicks'),
    Input('umap-graphic-cell-types-etacs', 'restyleData'),
    Input('all-cell-type-checklist', 'value'),
    Input('cell-type-checklist', 'value')
    )

def update_graph(gene_value, expression_data_value, dot_size_slider_value, umap_graphic_gene_slider, color_scale_dropdown_value, first_per_button_click, ninty_ninth_per_button_click, cell_type_fig_restyle_data, all_cell_type_checklist, cell_type_checklist):

    input_id = ctx.triggered_id
    global metadata
    if metadata is not None:
        #set initial gene value to be equal to default gene
        if gene_value is None:
            gene_value = default_gene

        #check if gene value is in dataframe
        gene_value_in_df = gene_value in gene_list
        #set gene value to be equal to default gene if gene not in dataframe (assuming default gene is in dataframe)
        if not gene_value_in_df:
            gene_value = default_gene

        #first lower case gene value
        gene_value = gene_value.lower()

        #table to get gene_value from
        table = gene_lookup[gene_value]
        
        if expression_data_value is None:
            expression_data_value = default_expression_data_value
        #extract gene column from table
        gene_data = pd.read_sql(table, con=engine if expression_data_value == 'Normalized' else engine_counts, columns = [gene_value, 'barcode'])

        #subset expression data on selected cells [gene_value, meta_cols]
        gene_data = pd.merge(gene_data, metadata, on='barcode', how='inner')

        #percentile slider code
        percentile_values = np.quantile(gene_data[gene_value], [0.99, 0.01])
        df_gene_min = min(gene_data[gene_value])
        df_gene_max = max(gene_data[gene_value])
        if input_id == 'umap-graphic-gene-slider-etacs':
            lower_slider_value = min(umap_graphic_gene_slider)
            higher_slider_value = max(umap_graphic_gene_slider)
        elif input_id == 'first-percentile-button':
            lower_slider_value = percentile_values[1]
            higher_slider_value = max(umap_graphic_gene_slider)
        elif input_id == 'ninty-ninth-percentile-button':
            lower_slider_value = min(umap_graphic_gene_slider)
            higher_slider_value = percentile_values[0]
        elif (input_id == 'umap-graphic-cell-types-etacs') | (input_id == 'dot-size-slider-data-browser-etacs') | (input_id == 'cell-type-checklist') | (input_id == 'all-cell-type-checklist'):
            lower_slider_value = min(umap_graphic_gene_slider) if umap_graphic_gene_slider != None else percentile_values[1]
            higher_slider_value = max(umap_graphic_gene_slider) if umap_graphic_gene_slider != None else percentile_values[0]
        else:
            lower_slider_value = percentile_values[1]
            higher_slider_value = percentile_values[0]

        dot_size_slider_value = dot_size_slider_value if dot_size_slider_value != None else 3


        gene_data = gene_data.sort_values(by=['cell_type'], kind='mergesort', ascending=False)

        gene_data_filtered = pd.DataFrame()

        #reset selected cell types to display if user changes genes
        if input_id == 'gene-value-etacs':
            all_cell_type_checklist.insert(0, 'All')
            cell_type_checklist = sorted_cell_list

        if input_id == "cell-type-checklist":
            all_cell_type_checklist = ["All"] if set(cell_type_checklist) == set(sorted_cell_list) else []
        elif input_id == 'all-cell-type-checklist':
            cell_type_checklist = sorted_cell_list if all_cell_type_checklist else [sorted_cell_list[0]]
        
        for i in cell_type_checklist:
                gene_data_filtered = pd.concat([gene_data_filtered, gene_data[gene_data['cell_type'] == i]])
        
        #graphs
        #sort dff based on cells highest expressing to lowest expressing gene - makes the gene scatter plot graph highest expressing cells on top of lower expressing cells
        gene_fig = px.scatter(gene_data_filtered.sort_values(by=[gene_value], kind='mergesort'),
                     #x coordinates
                     x='x',
                     #y coordinates
                     y='y',
                     color = gene_value if gene_value != None else default_gene,
                     hover_name = 'cell_type',
                     hover_data = {'x': False, 'y': False, 'cell_type': False},
                     range_color=
                     #min of color range
                     [lower_slider_value, 
                     #max of color range
                     higher_slider_value],
                     color_continuous_scale = color_scale_dropdown_value,
                     labels = {gene_value: gene_value.capitalize() + ' expression'}
                     )
        gene_fig.update_traces(
            marker=dict(
                size=dot_size_slider_value, 
                line=dict(width=0)
                )
            )
        gene_fig.update_layout(
            autosize = True,
            title = {
                'text': '<b>' + gene_value.capitalize() + '</b>',
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
            yaxis={'visible': False, 'showticklabels': False, 'scaleanchor': 'x', 'scaleratio': 1.0},
            margin={'l': 10, 'r': 10},
            plot_bgcolor = "white"
            )
        gene_fig.update_coloraxes(
            colorbar_title_text=''
            )

        cell_type_fig = px.scatter(gene_data,
                        x='x',
                        #x coordinates
                        y='y',
                        color = 'cell_type',
                        color_discrete_sequence = color_list,
                        #color_discrete_map = {'Other': 'lightgray'}, 
                        hover_name = 'cell_type',
                        hover_data = {'x': False, 'y': False, 'cell_type': False}
                    )
        cell_type_fig.update_traces(
            marker=dict(
                size=dot_size_slider_value, 
                line=dict(width=0)
                )
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
            showlegend = False,
            #legend={'title': '', 'entrywidthmode': 'pixels', 'entrywidth': 30, 'traceorder': 'reversed', 'itemsizing': 'constant'},
            margin={'l':10, 'r': 10},
            xaxis={'visible': False, 'showticklabels': False},
            yaxis={'visible': False, 'showticklabels': False, 'scaleanchor': 'x', 'scaleratio': 1.0},
            plot_bgcolor = "white"
            )

        cell_type_fig.for_each_trace(
            lambda trace: trace.update(visible='legendonly') if trace.name not in cell_type_checklist else (),
            )

        percentile_marks = {percentile_values[0]: '99th', percentile_values[1]: '1st'}



        return gene_fig, cell_type_fig, gene_value.capitalize(), expression_data_value, dot_size_slider_value, df_gene_min, df_gene_max, percentile_marks, [lower_slider_value, higher_slider_value], all_cell_type_checklist, cell_type_checklist
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
    return fig, fig, None, None, None, 3, 0, 100, [], [], html.H3(''), default_slider_marks, [default_percentiles[1], default_percentiles[0]], all_cell_type_checklist, cell_type_checklist

