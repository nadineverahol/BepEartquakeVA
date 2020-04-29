import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import geopandas as gpd
import geoplot as gplt
from shapely.geometry import Point
import plotly.graph_objects as go
from datetime import datetime as dt
import plotly.express as px
import json, urllib, time, requests
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, OPTICS
from haversine import haversine

start = time.time()

# Earthquakes from the year 2000 with minmag=2.5 and maxdepth=100km
df = pd.read_csv('data.csv')

# Make month and attribute, also making timestamp column actual timestamps and not strings
#df['month'] = [timestamp[5:7] for timestamp in df['timestamp']]
#df['day'] = [timestamp[8:10] for timestamp in df['timestamp']]
#df['month'] = df['month'].astype(int)
#df['day'] = df['day'].astype(int)
df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y/%m/%d %H:%M:%S")


px.set_mapbox_access_token("pk.eyJ1IjoidHJvdzEyIiwiYSI6ImNrOWNvOGpiajAwemozb210ZGttNXpoemUifQ.HtK_x39UnnD2_bXveR9nsQ")
#fig = px.scatter_mapbox(df, lat='lat', lon='long', color='mag', size='significance', hover_name='timestamp',
#                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=10, zoom=0, opacity=0.8)



# Dashboard
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([


    # for time range filtering
    dcc.DatePickerRange(
        id='date-range',
        min_date_allowed=dt(2000, 1, 1),
        max_date_allowed=dt(2020, 3, 31),
        # initial_visible_month=dt(2000, 1, 1),
        start_date=dt(2011, 1, 1).date(),
        end_date=dt(2011, 12, 31).date(),
        calendar_orientation='vertical'
    ),

    # for minimum magnitude selection (if None, plot cubic 0 on map)
    dcc.Input(
        id='min-magnitude',
        type='number',
        placeholder='input number',
        min=1,
        max=10,
    ),

    dcc.Input(
        id='number-of-clusters',
        type='number',
        placeholder='fill in number of clusters',
        min='2',
        max='100'
    ),

    dcc.Dropdown(
        id='main-map-selector',
        options=[
            {'label': 'Scatterplot', 'value': 'Scatter'},
            {'label': 'Density map', 'value': 'Densitymap'},
            {'label': 'K-means Clustering', 'value': 'K-means-Clustering'},
            {'label': 'Agglomerative Hierarchical Clustering', 'value': 'Agglomerative'},
            {'label': 'Density based spatial clustering', 'value': 'DBSCAN'},
            {'label': 'OPTICS clustering', 'value': 'OPTICS'}
        ],
        value='Scatter',
        multi=False,
        style={'height': 50, 'width': 200},
        optionHeight=50,
        placeholder="Select visualization"
    ),

    dcc.Graph(id='graph-main',
              style={'height': 600,
                     'width': 1200}),

])


@app.callback(
    Output('graph-main', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('min-magnitude', 'value'),
     Input('main-map-selector', 'value'),
     Input('number-of-clusters', 'value')])
def update_figure(start_date, end_date, value, option, n_clusters):
    if option is None:
        return {}

    if option == 'Scatter':
        if value is None or value > df['mag'].max():
            return {}

        else:
            filtered_df = df[(df.timestamp.between(start_date, end_date)) & (df.mag >= value)]
            fig = px.scatter_mapbox(filtered_df, lat='lat', lon='long', color='mag', range_color=[2.5, 10],
                                    size='significance', hover_name='timestamp',
                                    color_continuous_scale='Bluered', size_max=10, zoom=1, opacity=0.6)
            return fig
    if option == 'Densitymap':
        if value is None or value > df['mag'].max():
            return {}

        else:
            filtered_df = df[(df.timestamp.between(start_date, end_date)) & (df.mag >= value)]
            fig = px.density_mapbox(filtered_df, lat='lat', lon='long', z='mag', radius=10, zoom=1,
                                    center=dict(lat=0, lon=0))

            return fig

    if option == 'K-means-Clustering':
        if value is None or value > df['mag'].max() or n_clusters is None:
            return {}
        else:
            filtered_df = df[(df.timestamp.between(start_date, end_date)) & (df.mag >= value)]
            kmeans = KMeans(n_clusters=n_clusters)
            kmeans.fit(filtered_df[['long', 'lat']].to_numpy())
            filtered_df['cluster_nr'] = kmeans.predict(filtered_df[['long', 'lat']].to_numpy())

            fig = px.scatter_mapbox(filtered_df, lat='lat', lon='long', color='cluster_nr',
                                    size='significance', hover_name='timestamp',
                                    size_max=10, zoom=1, opacity=0.6)

            return fig

    if option == 'Agglomerative':
        if value is None or value > df['mag'].max() or n_clusters is None:
            return {}
        else:
            filtered_df = df[(df.timestamp.between(start_date, end_date)) & (df.mag >= value)]
            agglomerative = AgglomerativeClustering(n_clusters=n_clusters, distance_threshold=None)
            agglomerative.fit(filtered_df[['long', 'lat']].to_numpy())
            filtered_df['agglo_cluster'] = agglomerative.labels_

            fig = px.scatter_mapbox(filtered_df, lat='lat', lon='long', color='agglo_cluster',
                                    size='significance', hover_name='timestamp',
                                    size_max=10, zoom=1, opacity=0.6)

            return fig

    if option == 'DBSCAN':
        if value is None or value > df['mag'].max():
            return {}
        else:
            filtered_df = df[(df.timestamp.between(start_date, end_date)) & (df.mag >= value)]
            x_array = filtered_df[['long', 'lat']].to_numpy()
            # 50/6371 is 50km distance between points in radians
            db = DBSCAN(eps=100/6371., min_samples=5, algorithm='auto', metric='haversine').fit(np.radians(x_array))
            filtered_df['DBSCAN_cluster'] = db.labels_

            fig = px.scatter_mapbox(filtered_df, lat='lat', lon='long', color='DBSCAN_cluster',
                                    size='significance', hover_name='timestamp',
                                    size_max=10, zoom=1, opacity=0.6)

            return fig

    if option == 'OPTICS':
        if value is None or value > df['mag'].max():
            return {}
        else:
            filtered_df = df[(df.timestamp.between(start_date, end_date)) & (df.mag >= value)]
            x_array = filtered_df[['long', 'lat']].to_numpy()
            optics = OPTICS(min_samples=5, eps=100/6371., metric='haversine').fit(np.radians(x_array))
            filtered_df['Optics'] = optics.labels_

            fig = px.scatter_mapbox(filtered_df, lat='lat', lon='long', color='Optics',
                                    size='significance', hover_name='timestamp',
                                    size_max=10, zoom=1, opacity=0.6)

            return fig


if __name__ == '__main__':
    app.run_server(debug=True)
