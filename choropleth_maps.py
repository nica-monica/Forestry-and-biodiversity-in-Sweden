import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.dependencies import Output, Input

import pandas as pd
import geopandas as gpd
import json

# Load your dataframe

df = pd.read_csv('https://raw.githubusercontent.com/nica-monica/Forestry-and-biodiversity-in-Sweden/main/pivot_municipality_org_pbservations.csv')
sweden_kommun = gpd.read_file('https://raw.githubusercontent.com/nica-monica/Forestry-and-biodiversity-in-Sweden/main/sweden_kommun_province.geojson')

back_geojson = sweden_kommun.to_json()
g = json.loads(back_geojson)

# Define the available options for the Measure radio buttons
measure_options = [
    {'label': 'All Species', 'value': 'All Species'},
    {'label': 'Redlisted Species', 'value': 'Redlisted Species'},
    {'label': 'Most Vulnerable Species*', 'value': 'Most Vulnerable Species*'}
]
filtered_df=df.copy()
filtered_df = filtered_df[filtered_df['Measure'].isin([ 'All Species'])]

column_names = ['Vascular Plants', 'Lichens', 'Mushrooms', 'Mosses', 'Insects', 'Invertebrates', 'Birds', 'Mammals']
color_schemes=['speed', 'Purples', 'Oranges', 'PuBuGn', 'YlOrBr', 'RdPu', 'YlGnBu', 'YlOrRd']

# Create the Dash app and set up the layout. the meta tags allow viewing on mobiles
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
server=app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Biodiversity Maps of Swedish Forests",
                        className='text-center text-primary mb-4'),
                width=12)
    ]),
    dbc.Row([
        html.P('The maps display the number of unique species observed in each municipality. Use the options below to see all species or select the ones that are redlisted.'),
        html.P('*Most vulnerable species are defined as having Critically Endangered or Endangered status.'),
    ]),
    html.Div(style={'margin-bottom': '20px'}),
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                id='measure-radio',
                options=measure_options,
                value='All Species' , labelStyle={'display': 'inline-block', 'margin-right': '10px'}     # Initial value of the radio buttons

            )
        ],  width=12)
    ]),
    html.Div(style={'margin-bottom': '20px'}),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='map-plants', figure={})
        ], width={'size': 3}),
        dbc.Col([
            dcc.Graph(id='map-mushrooms', figure={})
        ], width={'size': 3}),
        dbc.Col([
            dcc.Graph(id='map-lichens', figure={})
        ], width={'size': 3}),
        dbc.Col([
            dcc.Graph(id='map-mosses', figure={})
        ], width={'size': 3})

        ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='map-insects', figure={})
        ], width={'size': 3}),
        dbc.Col([
            dcc.Graph(id='map-invertebrates', figure={})
        ], width={'size': 3}),
        dbc.Col([
            dcc.Graph(id='map-birds', figure={})
        ], width={'size': 3}),
        dbc.Col([
            dcc.Graph(id='map-mammals', figure={})
        ], width={'size': 3})
    ]),
    # dcc.Store(id='measure-dropdown'),
	# dcc.Graph(id='map-plants'),
	# dcc.Graph(id='map-mushrooms'),
])

@app.callback(
    [
     dash.dependencies.Output('map-plants', 'figure'),
     dash.dependencies.Output('map-mushrooms', 'figure'),
     dash.dependencies.Output('map-lichens', 'figure'),
     dash.dependencies.Output('map-mosses', 'figure'),
     dash.dependencies.Output('map-insects', 'figure'),
     dash.dependencies.Output('map-invertebrates', 'figure'),
     dash.dependencies.Output('map-birds', 'figure'),
     dash.dependencies.Output('map-mammals', 'figure')],
    [dash.dependencies.Input('measure-radio', 'value')]
)
def update_map_grid(selected_measure):
    # Filter the database based on the selected measure
    filtered_df=df.copy()
    filtered_df = filtered_df[filtered_df['Measure'].isin([ selected_measure])]

    # Create the choropleth maps for each graph
    figures = []
    for column , color in zip(column_names, color_schemes):
        fig = go.Figure(data=go.Choroplethmapbox(
            geojson=g,
            locations=filtered_df['Municipality Name'],
            z=filtered_df[column],
            featureidkey="properties.kom_namn",
            colorscale=color,  # You can specify your desired color scale here
            zmin=filtered_df[column].min(),
            zmax=filtered_df[column].max(),
            marker_opacity=0.7,
            marker_line_width=0,
            colorbar=dict(
                thickness=4, lenmode='fraction', len=0.8
            )
        ))

        fig.update_layout(
            mapbox_style="white-bg",
            mapbox_zoom=2.5,
            mapbox_center={"lat": 63, "lon": 14},
            margin={"r": 0.5, "t": 0.5, "l": 0.5, "b": 0.5},
            showlegend=False,
            autosize=False,
            width=230,
            height=300,
            title={
                'text': str(column),
                'y': 0.98,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }

        )

        figures.append(fig)

    return figures[0], figures[2], figures[1], figures[3], figures[4], figures[5], figures[6], figures[7]


# Run the Dash app

if __name__ == '__main__':
    app.run_server(debug=False)
