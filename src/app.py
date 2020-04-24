import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import geopandas as gpd
import geoplot as gplt
from shapely.geometry import Point
import plotly.graph_objects as go
import plotly.express as px
import json, urllib, time, requests
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

start = time.time()

# Earthquakes from the year 2000 with minmag=2.5 and maxdepth=100km
df = pd.read_csv("year_2000.csv")

# Make month attribute for slider
df['month'] = [timestamp[5:7] for timestamp in df['timestamp']]
df['day'] = [timestamp[8:10] for timestamp in df['timestamp']]
df['month'] = df['month'].astype(int)
df['day'] = df['day'].astype(int)


px.set_mapbox_access_token("pk.eyJ1IjoidHJvdzEyIiwiYSI6ImNrOWNvOGpiajAwemozb210ZGttNXpoemUifQ.HtK_x39UnnD2_bXveR9nsQ")
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


    dcc.Graph(id='graph-width-slider'),
    dcc.Slider(
        id='month-slider',
        min=df['month'].min(),
        max=df['month'].max(),
        value=df['month'].min(),
        marks={str(month): str(month) for month in df['month'].unique()},
        step=None

    ),

])

"""
app.layout = html.Div([
    dcc.Graph(id='graph-width-slider',
              style={'height': 600,
                     'width': 1200}),
    dcc.RangeSlider(
        id='month-slider',
        min=df['month'].min(),
        max=df['month'].max(),
        value=[df['month'].min(), df['month'].max()],
        marks={str(month): str(month) for month in df['month'].unique()},
        step=None,

    ),

])


@app.callback(
    Output('graph-width-slider', 'figure'),
    [Input('month-slider', 'value')])
def update_figure(selected_month):
    filtered_df = df[df.month.between(selected_month[0], selected_month[1])]
    fig = px.scatter_mapbox(filtered_df, lat='lat', lon='long', color='mag', range_color=[2.5,10],
                            size='significance', hover_name='timestamp',
                            color_continuous_scale='Bluered', size_max=10, zoom=1, opacity=0.6)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
