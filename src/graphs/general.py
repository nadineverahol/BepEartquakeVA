import pandas as pd
import plotly.express as px
from datetime import datetime as dt

def general_graph(data, option, magrange, n_clusters, colorscale):

    lon = [item['geometry']['coordinates'][0] for item in data]
    lat = [item['geometry']['coordinates'][1] for item in data]
    size = [item['properties']['sig'] for item in data]
    time = [dt.fromtimestamp(item['properties']['time'] / 1000) for item in data]
    mag = [item['properties']['mag'] for item in data]
    place = [item['properties']['place'] for item in data]
    sig = [item['properties']['sig'] for item in data]
    depth = [item['geometry']['coordinates'][2] for item in data]

    if option is None:
        return {}
    if option == 'Scatter':

        fig = px.scatter_mapbox(data, lat=lat, lon=lon, color=mag,
                                range_color=[2.5, 10],
                                size=sig, hover_name=time, hover_data=[depth],
                                color_continuous_scale=colorscale, size_max=14, zoom=0.8, opacity=0.6,
                                labels={'color': "Magnitude (M)",
                                        'lat': "latitude",
                                        'lon': "longitude",
                                        'size': 'Significance',
                                        'hover_data_0': 'depth (km)'})

        return fig

    if option == 'Densitymap':

        fig = px.density_mapbox(data, lat=lat, lon=lon, radius=5, zoom=0.6,
                                color_continuous_scale=colorscale)

        return fig

    if option == 'ParallelCoordinates':
        fig = px.parallel_coordinates(data, color=mag, color_continuous_scale=colorscale,
                                      dimensions=[mag, depth, sig],
                                      color_continuous_midpoint=2)

        return fig

    else:
        return {}