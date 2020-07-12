import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, OPTICS
from datetime import datetime as dt
import numpy as np

def clustering_graph(data, option, min_mag, n_clusters, colorscale, location):

    if option is None:
        return {}

    if option == "K-means-Clustering":
        df = pd.DataFrame()
        kmeans = KMeans(n_clusters=n_clusters)
        df['long'] = [item['geometry']['coordinates'][0] for item in data]
        df['lat'] = [item['geometry']['coordinates'][1] for item in data]
        df['mag'] = [item['properties']['mag'] for item in data]
        df['time'] = [dt.fromtimestamp(item['properties']['time']/1000) for item in data]

        kmeans.fit(df[['long', 'lat']].to_numpy())
        df['cluster_nr'] = kmeans.predict(df[['long', 'lat']].to_numpy())

        fig = px.scatter_mapbox(df, lat='lat', lon='long', color='cluster_nr',
                                size='mag', hover_name='time', size_max=10, zoom=0.8, opacity=0.7,
                                labels={'cluster_nr': "Cluster Number",
                                        'lat': "latitude",
                                        'lon': "longitude",
                                        'size': 'Magnitude'}
                                )

        return fig

    if option == "Agglomerative":
        df = pd.DataFrame()
        agglo = AgglomerativeClustering(n_clusters=n_clusters, distance_threshold=None)
        df['long'] = [item['geometry']['coordinates'][0] for item in data]
        df['lat'] = [item['geometry']['coordinates'][1] for item in data]
        df['mag'] = [item['properties']['mag'] for item in data]
        df['time'] = [dt.fromtimestamp(item['properties']['time'] / 1000) for item in data]
        agglo.fit(df[['long', 'lat']].to_numpy())
        df['cluster_nr'] = agglo.labels_

        fig = px.scatter_mapbox(df, lat='lat', lon='long', color='cluster_nr',
                                size='mag', hover_name='time',
                                size_max=10, zoom=0.8, opacity=0.7,
                                labels={'cluster_nr': "Cluster Number",
                                        'lat': "latitude",
                                        'lon': "longitude",
                                        'size': 'Magnitude'}
                                )

        return fig

    if option == "DBSCAN":
        df = pd.DataFrame()
        df['long'] = [item['geometry']['coordinates'][0] for item in data]
        df['lat'] = [item['geometry']['coordinates'][1] for item in data]
        df['mag'] = [item['properties']['mag'] for item in data]
        df['time'] = [dt.fromtimestamp(item['properties']['time'] / 1000) for item in data]

        x_array = df[['long', 'lat']].to_numpy()
        db = DBSCAN(eps=100 / 6371., min_samples=4, algorithm='auto', metric='haversine').fit(np.radians(x_array))
        df['DBSCAN_cluster'] = db.labels_

        fig = px.scatter_mapbox(df, lat='lat', lon='long', color='DBSCAN_cluster', size='mag',
                                hover_name='time',
                                size_max=10, zoom=0.8, opacity=0.7,
                                labels={'DBSCAN_cluster': "Cluster Number",
                                        'lat': "latitude",
                                        'lon': "longitude",
                                        'size': 'Magnitude'}
                                )

        return fig


    if option == "OPTICS":
        df = pd.DataFrame()
        df['long'] = [item['geometry']['coordinates'][0] for item in data]
        df['lat'] = [item['geometry']['coordinates'][1] for item in data]
        df['mag'] = [item['properties']['mag'] for item in data]
        df['time'] = [dt.fromtimestamp(item['properties']['time'] / 1000) for item in data]

        x_array = df[['long', 'lat']].to_numpy()

        optics = OPTICS(min_samples=4, eps=100 / 6371., metric='haversine').fit(np.radians(x_array))
        df['optics_cluster'] = optics.labels_

        fig = px.scatter_mapbox(df, lat='lat', lon='long', color='optics_cluster', size='mag',
                                hover_name='time', size_max=10, zoom=0.8, opacity=0.7,
                                labels={'optics_cluster': "Cluster Number",
                                        'lat': "latitude",
                                        'lon': "longitude",
                                        'size': 'Magnitude'}
                                )

        return fig

    return {}

