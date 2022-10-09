# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.




from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import numpy as np

import pandas as pd

app = Dash(__name__)

#df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')
df = pd.read_csv('file://localhost/Users/nolanhorner/Documents/UCSF/computer-projects/mTEC-eTAC-atlases/test-data/WT_KO_thymus_subset.csv')

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                df['cell_type'].unique(),
                'Tuft',
                id='cell-type-value'
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                np.insert(df['genotype'].unique(), 0, 'All'),
                'WT',
                id='genotype-value'
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='umap-graphic'),

])


@app.callback(
    Output('umap-graphic', 'figure'),
    Input('cell-type-value', 'value'),
    Input('genotype-value', 'value'),
    #Input('gene-value', 'value')
    )
def update_graph(cell_type_value, genotype_value, gene_value = 'Prr15l'):

    dff = df[df['genotype'] == genotype_value] if genotype_value != 'All' else df
    fig = px.scatter(x=dff['x'],
        #x coordinates
                     y=dff['y'],
                     color = dff[gene_value]
                     #y coordinates
                     #hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name']
                     )
    fig.update_layout(width = 800, height = 800, title = gene_value)

    #fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

