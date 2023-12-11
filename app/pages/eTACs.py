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
    host = 'gardner-lab'
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

#dataset_list = metadata.dataset.unique()
if hasattr(metadata, 'dataset'):
    dataset_list = np.insert(metadata.dataset.unique(), 0, 'All') if metadata.dataset.unique().size >= 1 else metadata.dataset.unique()
else:
    dataset_list = ['All']

default_dataset_value = dataset_list[0]

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
 'darkblue',
 'grey',
 'peru']

sorted_cell_list = metadata.celltype.unique().copy()
sorted_cell_list.sort()

checklist_children = [{"label": html.Div([
    html.Button(disabled = True, style={'background-color': color_list[i], 'padding-left': 10}, className = 'icon-button'),
    html.Div(sorted_cell_list[i], style={'font-size': 12, 'padding-left': 5, 'color': 'black'}),
    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}), "value": sorted_cell_list[i]} for i in range(len(sorted_cell_list))]

if len(color_list) >= len(metadata.celltype.unique()):
    color_list = color_list[0:len(metadata.celltype.unique())]
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
                html.Img(src='static/gardner-lab-logo-200w-transparent-new.png', id = 'lab-logo'),
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
                    # html.A(
                    # html.Button('JCs', className='page-buttons'),
                    # href='/jcs'
                    # ),
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
                #dropdown for dataset
                html.H3('Dataset:', id='dataset-headline'),
                dcc.Dropdown(dataset_list, placeholder = 'Select a dataset...', value='All', id='dataset-value-etacs'),
                #dropdown for counts vs normalized
                html.H3('Expression data:', id='expression-data-headline'),
                dcc.Dropdown(['Raw counts', 'Normalized'], placeholder = 'Select a visualization...', id='expression-data-value-etacs'),
                #slider for dot size
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
                                config = {
                                    'toImageButtonOptions': {
                                        'format': 'svg',
                                        'filename': 'etac_gene_expression',
                                        'height': 1080,
                                        'width': 1080,
                                        'scale': 1
                                    },
                                    'displaylogo': False,
                                    'modeBarButtonsToAdd': [
                                         # {'name': 'color toggler', 'icon': 'icon1',
                                         #  'click': "function (gd) {Plotly.toImage(gd, { format: 'png', width: 2100, height: 900 })}"
                                            # var newColor = colors[Math.floor(3 * Math.random())]
                                            # Plotly.restyle(gd, 'line.color', newColor)
                                        #  }},
                                        # {
                                        #   'name': 'button1',
                                        #   'icon': Plotly.Icons.pencil,
                                        #   'direction': 'up',
                                        #   click: function(gd) {alert('button1')
                                        # }
                                          # }
                                         ],
                                    'modeBarButtonsToRemove': ['pan2d','select2d','lasso2d','resetScale2d']
                                },
                                id='umap-graphic-gene-etacs')
                        ], style={'width': '42%', 'marginRight': '1.5%'}),
                        html.Div([
                            dcc.Graph(figure = px.scatter(x = [0], y=[0], color_discrete_sequence=['white']).update_layout(
                                xaxis={'visible': False, 'showticklabels': False},
                                yaxis={'visible': False, 'showticklabels': False},
                                plot_bgcolor = "white",
                                width=650, height=650),
                                config = {
                                    'toImageButtonOptions': {
                                        'format': 'svg',
                                        'filename': 'etac_cell_types',
                                        'height': 1080,
                                        'width': 1080,
                                        'scale': 1
                                    },
                                    'displaylogo': False,
                                    'modeBarButtonsToRemove': ['pan2d','select2d','lasso2d','resetScale2d']
                                },
                                id='umap-graphic-cell-types-etacs')
                        ], style={'width': '35%', 'marginLeft': '1.5%'}),
                        html.Div([
                            html.Div([
                                html.Button('All', id = 'all-cell-type-button-etacs'),
                                html.Button('Deselect', id = 'no-cell-type-button-etacs')
                            ], style = {'marginBottom': '2%', 'display': 'flex', 'justify-content': 'center'}),
                            dcc.Checklist(checklist_children, sorted_cell_list[0:len(sorted_cell_list)], labelStyle = {'display': 'flex'}, id='cell-type-checklist-etacs'),
                            html.Button('Legend', id = 'cell-type-legend-button-etacs', style = {'marginTop': '1%'}),
                        ], style = {'marginTop': '1%', 'marginRight': '2%'}),
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
    Output('dataset-value-etacs', 'value'),
    Output('dot-size-slider-data-browser-etacs', 'value'),
    Output('umap-graphic-gene-slider-etacs', 'min'),
    Output('umap-graphic-gene-slider-etacs', 'max'),
    Output('umap-graphic-gene-slider-etacs', 'marks'),
    Output('umap-graphic-gene-slider-etacs', 'value'),
    Output('cell-type-checklist-etacs', 'value'),
    Input('gene-value-etacs', 'value'),
    Input('expression-data-value-etacs', 'value'),
    Input('dataset-value-etacs', 'value'),
    Input('dot-size-slider-data-browser-etacs', 'value'),
    Input('umap-graphic-gene-slider-etacs', 'value'),
    Input('color-scale-dropdown', 'value'),
    Input('first-percentile-button', 'n_clicks'),
    Input('ninty-ninth-percentile-button', 'n_clicks'),
    Input('umap-graphic-cell-types-etacs', 'restyleData'),
    Input('all-cell-type-button-etacs', 'n_clicks'),
    Input('no-cell-type-button-etacs', 'n_clicks'),
    Input('cell-type-checklist-etacs', 'value'),
    Input('cell-type-legend-button-etacs', 'n_clicks')
    )

def update_graph(gene_value, expression_data_value, dataset_value, dot_size_slider_value, umap_graphic_gene_slider, color_scale_dropdown_value, first_per_button_click, ninty_ninth_per_button_click, cell_type_fig_restyle_data, all_cell_type_button_click, no_cell_type_button_click, cell_type_checklist, cell_type_legend_button):

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

        #set default genotype value to WT
        if dataset_value is None:
            dataset_value = default_dataset_value

        #makes dataset value into list of selected datasets
        if (dataset_value != 'All') & (len(dataset_list) > 1):
            metadata_subset = metadata[metadata.dataset == dataset_value]
        else:
            metadata_subset = metadata

        # #change genotype dropdown list depending on dataset input value
        # genotype_list_subset = metadata_subset.genotype.unique()
        # if genotype_list_subset.size == 0:
        #     raise ValueError("No genotypes found in this dataset...")
        # elif genotype_list_subset.size > 1:
        #     genotype_list_subset = np.insert(genotype_list_subset, 0, 'All')

        # #set default genotype value to WT
        # if genotype_value is None or genotype_value not in genotype_list_subset:
        #     genotype_value = default_genotype_value if default_genotype_value in genotype_list_subset else genotype_list_subset[0]
        # #makes genotype value into list of selected genotypes
        # if genotype_value != 'All':
        #     metadata_subset = metadata_subset[metadata_subset.genotype == genotype_value]
        # else:
        #     metadata_subset = metadata_subset

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
        elif (input_id == 'umap-graphic-cell-types-etacs') | (input_id == 'dot-size-slider-data-browser-etacs') | (input_id == 'cell-type-checklist-etacs') | (input_id == 'all-cell-type-button-etacs') | (input_id == 'no-cell-type-button-etacs'):
            lower_slider_value = min(umap_graphic_gene_slider) if umap_graphic_gene_slider != None else percentile_values[1]
            higher_slider_value = max(umap_graphic_gene_slider) if umap_graphic_gene_slider != None else percentile_values[0]
        else:
            lower_slider_value = percentile_values[1]
            higher_slider_value = percentile_values[0]

        dot_size_slider_value = dot_size_slider_value if dot_size_slider_value != None else 3


        gene_data = gene_data.sort_values(by=['celltype'], kind='mergesort', ascending=False)

        gene_data_filtered = pd.DataFrame()

        if (input_id == 'no-cell-type-button-etacs'):
            cell_type_checklist = []

        if input_id == 'all-cell-type-button-etacs':
            cell_type_checklist = sorted_cell_list

        for i in cell_type_checklist:
                gene_data_filtered = pd.concat([gene_data_filtered, gene_data[gene_data['celltype'] == i]])
        
        #graphs
        #sort dff based on cells highest expressing to lowest expressing gene - makes the gene scatter plot graph highest expressing cells on top of lower expressing cells
        if len(cell_type_checklist) == 0:
            fig = px.scatter(x=[0],
                 y=[0],
                 color_discrete_sequence=['white']
                 )
            fig.update_layout(
                xaxis={'visible': False, 'showticklabels': False},
                yaxis={'visible': False, 'showticklabels': False},
                margin = dict(l=50, r=50, t=50, b=50, pad=4),
                plot_bgcolor = "white",
                hovermode = False
                )
            gene_fig = fig
            cell_type_fig = fig
        else:
            gene_fig = px.scatter(gene_data_filtered.sort_values(by=[gene_value], kind='mergesort'),
                         #x coordinates
                         x='x',
                         #y coordinates
                         y='y',
                         color = gene_value if gene_value != None else default_gene,
                         hover_name = 'celltype',
                         hover_data = {'x': False, 'y': False, 'celltype': False},
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
                            color = 'celltype',
                            color_discrete_sequence = color_list,
                            #color_discrete_map = {'Other': 'lightgray'}, 
                            hover_name = 'celltype',
                            hover_data = {'x': False, 'y': False, 'celltype': False}
                        )
            cell_type_fig.update_traces(
                marker=dict(
                    size=dot_size_slider_value, 
                    line=dict(width=0)
                    )
                )
            if cell_type_legend_button is None:
                show_cell_legend = False
            elif cell_type_legend_button % 2 == 0:
                show_cell_legend = False
            else:
                show_cell_legend = True
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
                showlegend = show_cell_legend,
                legend={'title': '', 'entrywidthmode': 'pixels', 'entrywidth': 30, 'traceorder': 'reversed', 'itemsizing': 'constant'},
                margin={'l':10, 'r': 10},
                xaxis={'visible': False, 'showticklabels': False},
                yaxis={'visible': False, 'showticklabels': False, 'scaleanchor': 'x', 'scaleratio': 1.0},
                plot_bgcolor = "white"
                )

            cell_type_fig.for_each_trace(
                lambda trace: trace.update(visible='legendonly') if trace.name not in cell_type_checklist else (),
                )

        percentile_marks = {percentile_values[0]: '99th', percentile_values[1]: '1st'}

        return gene_fig, cell_type_fig, gene_value.capitalize(), expression_data_value, dataset_value, dot_size_slider_value, df_gene_min, df_gene_max, percentile_marks, [lower_slider_value, higher_slider_value], cell_type_checklist
        #gene_slider
    fig = px.scatter(x=[0],
                 y=[0],
                 color_discrete_sequence=['white']
                 )
    fig.update_layout(
        xaxis={'visible': False, 'showticklabels': False},
        yaxis={'visible': False, 'showticklabels': False},
        margin = dict(l=50, r=50, t=50, b=50, pad=4),
        plot_bgcolor = "white",
        hovermode = False
        )
    default_percentiles = np.quantile([0, 100], [0.99, 0.01])
    default_slider_marks = {int(default_percentiles[0]): '99th', int(default_percentiles[1]): '1st'}
    return fig, fig, None, None, None, None, 3, 0, 100, [], [], html.H3(''), default_slider_marks, [default_percentiles[1], default_percentiles[0]], cell_type_checklist

