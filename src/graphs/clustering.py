import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans 
import geopandas


def clustering_graph(data, option, magrange, n_clusters, location):

    lon = [item['geometry']['coordinates'][0] for item in data]
    lat = [item['geometry']['coordinates'][1] for item in data]
    size = [item['properties']['sig'] for item in data]
    time = [item['properties']['time'] for item in data]
    mag = [item['properties']['mag'] for item in data]
    place = [item['properties']['place'] for item in data]
    sig = [item['properties']['sig'] for item in data]

    if option is None:
        return {}
    if option == 'K-means-Clustering':
        df = geopandas.GeoDataFrame(data)
        kmeans = KMeans(n_clusters=n_clusters)
        kmeans.fit(df[['lon', 'lat']].to_numpy())
        df['cluster_nr'] = kmeans.predict(df[['long', 'lat']].to_numpy())

        fig = px.scatter_mapbox(df, lat='lat', lon='long', color='cluster_nr',
                                size='significance', hover_name='timestamp',
                                size_max=10, zoom=1, opacity=0.6)
        return fig
    return {}

