import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import geopandas as gpd
# import geoplot as gplt
from shapely.geometry import Point
from plotly import graph_objects as go
from datetime import datetime as dt
import plotly.express as px
import json
import urllib
import time
import requests
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

start = time.time()

# Earthquakes from the year 2000 with minmag=2.5 and maxdepth=100km
df = pd.read_csv('data.csv')

# Make month and attribute, also making timestamp column actual timestamps and not strings
df['month'] = [timestamp[5:7] for timestamp in df['timestamp']]
df['day'] = [timestamp[8:10] for timestamp in df['timestamp']]
df['month'] = df['month'].astype(int)
df['day'] = df['day'].astype(int)
df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y/%m/%d %H:%M:%S")
#

px.set_mapbox_access_token(
    "pk.eyJ1IjoidHJvdzEyIiwiYSI6ImNrOWNvOGpiajAwemozb210ZGttNXpoemUifQ.HtK_x39UnnD2_bXveR9nsQ")
fig = px.scatter_mapbox(df, lat='lat', lon='long', color='mag', size='significance', hover_name='timestamp',
                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=10, zoom=0, opacity=0.8)


# Dashboard
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

"""
app.layout = html.Div(children=[
    html.H1(children='Earthquake visualization tool'),
    html.Div(children='''
    A visualization tool for the earthquakes BEP, by Jeroen Gommers, Nadine Hole and Wessel Krenn.
    '''),


    dcc.Graph(id='graph-width-slider',
              style={'height': 600,
                     'width': 1200),
    dcc.Slider(
        id='month-slider',
        min=df['month'].min(),
        max=df['month'].max(),
        value=df['month'].min(),
        marks={str(month): str(month) for month in df['month'].unique()},
        step=None

    ),
  ]
)
"""
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div([


    # for time range filtering
    dcc.DatePickerRange(
        id='date-range',
        min_date_allowed=dt(2000, 1, 1),
        max_date_allowed=dt(2020, 3, 31),
        #initial_visible_month=dt(2000, 1, 1),
        start_date=dt(2000, 1, 1).date(),
        end_date=dt(2000, 1, 2).date(),
        calendar_orientation='vertical'
    ),

    # for minimum magnitude selection (if None, plot cubic 0 on map)
    dcc.Input(
        id='min-magnitude',
        type='number',
        placeholder='input number',
        min=1,
        max=10

    ),
    dcc.Graph(id='graph-main',
              style={'height': 600,
                     'width': 1200}),
])


@app.callback(
    Output('graph-main', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('min-magnitude', 'value')])
def update_figure(start_date, end_date, value):
    if value == None:

        # lon and lat together make a 0 on the map
        fig = go.Figure(go.Scattermapbox(mode='markers+lines',
                                         lon=[0, 0, -20, -20, 0],
                                         lat=[50, -50, -50, 50, 50],
                                         marker={'size': 30}))
        fig.update_layout(
            mapbox={
                'center': {'lon': -10, 'lat': 0},
                'style': "open-street-map",
                'zoom': 1
            }
        )

        return fig

    else:
        filtered_df = df[(df.timestamp.between(
            start_date, end_date)) & (df.mag >= value)]

        fig = px.scatter_mapbox(filtered_df, lat='lat', lon='long', color='mag', range_color=[2.5, 10],
                                size='significance', hover_name='timestamp',
                                color_continuous_scale='Bluered', size_max=10, zoom=1, opacity=0.6)
        return fig


if __name__ == '__main__':
    app.run_server(debug=True)
