import base64
import io

from dash import Dash, dcc, html, callback, Input, Output, State, ctx
import dash
import plotly.express as px
import numpy as np
import sqlalchemy as db
import plotly.graph_objects as go

import pandas as pd
import csv
import os
import boto3
import sys

dash.register_page(__name__)

##=========================Global variables=========================##
database = 'lymphnode'
if ('LOCALDEV' in os.environ) | ('LOCALDEPLOY' in os.environ):
    host = 'localhost'
    user = 'root'
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
 'indigo',
 'peru']

sorted_cell_list = metadata.cell_type.unique().copy()
sorted_cell_list.sort()

cell_colors = dict(zip(sorted_cell_list, color_list))

checklist_children = [{"label": html.Div([
    html.Button(disabled = True, style={'background-color': color_list[i], 'padding-left': 10}, className = 'icon-button'),
    html.Div(sorted_cell_list[i], style={'font-size': 12, 'padding-left': 5, 'color': 'black'}),
    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}), "value": sorted_cell_list[i]} for i in range(len(sorted_cell_list))]

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
                dcc.Dropdown(['Log1p', 'Normalized'], placeholder = 'Select a visualization...', id='expression-data-value-etacs'),
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
                                    'scrollZoom': True,
                                    'displaylogo': False,
                                    'modeBarButtonsToRemove': ['select2d','lasso2d','resetScale2d']
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
                                    'scrollZoom': True,
                                    'displaylogo': False,
                                    'modeBarButtonsToRemove': ['select2d','lasso2d','resetScale2d']
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


        gene_data = gene_data.sort_values(by=['cell_type'], kind='mergesort', ascending=False)

        gene_data_filtered = pd.DataFrame()

        if (input_id == 'no-cell-type-button-etacs'):
            cell_type_checklist = []

        if input_id == 'all-cell-type-button-etacs':
            cell_type_checklist = sorted_cell_list
        
        if dataset_value != "All":
            unselected = gene_data[~gene_data.cell_type.isin(cell_type_checklist) | (gene_data.dataset != dataset_value)]
            selected = gene_data[gene_data.cell_type.isin(cell_type_checklist) & (gene_data.dataset == dataset_value)]
        else:
            unselected = gene_data[~gene_data.cell_type.isin(cell_type_checklist)]
            selected = gene_data[gene_data.cell_type.isin(cell_type_checklist)]
        selected = selected.sort_values(by=["cell_type"], kind='mergesort', ascending=False)
        cell_types_to_plot = selected["cell_type"].unique()
        cell_types_to_plot.sort()
        color_list_copy = [cell_colors[cell_type] for cell_type in cell_types_to_plot]
        color_list_copy.reverse()

        
        #graphs
        #selected cells
        gene_fig_sel = px.scatter(
            selected.sort_values(by=[gene_value], kind='mergesort'),
            x='x',
            y='y',
            color = gene_value if gene_value != None else default_gene,
            hover_name = "cell_type",
            hover_data = {'x': False, 'y': False, gene_value: True},
            range_color=[lower_slider_value, higher_slider_value],
            color_continuous_scale = color_scale_dropdown_value,
            labels = {gene_value: gene_value.capitalize() + ' expression'},
        )
        gene_fig_sel.update_traces(
            marker=dict(
                size=dot_size_slider_value,
                line=dict(width=0, color='black')
                )
            )
        gene_fig_sel.update_coloraxes(colorbar_title_text='')

        #unselected cells
        gene_bg = go.Scattergl(  # Scattergl is faster for lots of points
            x=unselected['x'],
            y=unselected['y'],
            mode='markers',
            marker=dict(
                size=dot_size_slider_value,
                color='lightgrey',       # fixed grey
                line=dict(width=0)       # optional thin outline if you want: line=dict(width=0.3, color='rgba(0,0,0,0.2)')
            ),
            hoverinfo='skip',            # keep hovers clean
            showlegend=False
        )
        gene_selected = selected.sort_values(by=[gene_value], kind='mergesort')
        gene_fg = go.Scattergl(
            x=np.round(gene_selected['x'], 3),
            y=np.round(gene_selected['y'], 3),
            mode='markers',
            marker=dict(
                size=dot_size_slider_value,
                line=dict(width=0),  # outlines cost a lot; avoid or keep tiny
                color=np.round(gene_selected[gene_value].to_numpy(), 3),         # numeric array
                colorscale=color_scale_dropdown_value,
                cmin=lower_slider_value,
                cmax=higher_slider_value,
                showscale=True
            ),
            # minimal hover to cut payload; or set 'hoverinfo':'skip' if N is huge
            customdata=np.stack([gene_selected.cell_type.to_numpy()], axis=-1),
            hovertemplate=(
                f"<b>%{{customdata}}</b><br>"
                f"{gene_value.capitalize()}: %{{marker.color:.3g}}<extra></extra>"
            )
            # hoverinfo='skip'
        )

        # Assemble into figure
        gene_fig = go.Figure(data=[gene_bg, gene_fg])
        gene_fig.update_layout(
            # keep colorbar thin
            coloraxis_colorbar=dict(title='', thicknessmode='pixels', thickness=30),  # harmless even though we set showscale on trace
            xaxis=dict(visible=False, showticklabels=False),
            yaxis=dict(visible=False, showticklabels=False, scaleanchor='x', scaleratio=1.0),
            margin=dict(l=10, r=10),
            plot_bgcolor="white",
            dragmode='pan',
            showlegend=False,
            # preserve zoom/pan between updates in Dash (prevents full re-render)
            uirevision="gene-plot"
        )

        # Selected cells
        cell_type_fig_sel = px.scatter(
            selected,
            x='x',
            y='y',
            color="cell_type",
            color_discrete_sequence=color_list_copy,
            color_discrete_map={},
            hover_name = "cell_type",
            hover_data = {'x': False, 'y': False, "cell_type": False},
            render_mode="webgl",
        )
        cell_type_fig_sel.update_traces(
            marker=dict(
                size=dot_size_slider_value,
                line=dict(width=0, color="black")
            )
        )
        if cell_type_legend_button is None:
            show_cell_legend = False
        elif cell_type_legend_button % 2 == 0:
            show_cell_legend = False
        else:
            show_cell_legend = True

        # Assemble into figure
        cell_type_fig = go.Figure(gene_bg)    # put grey layer first (drawn underneath)
        for tr in cell_type_fig_sel.data:     # then add the colored layer (keeps coloraxis & colorbar)
            cell_type_fig.add_trace(tr)
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
            plot_bgcolor = "white",
            dragmode='pan',
            uirevision="celltype-plot"
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

