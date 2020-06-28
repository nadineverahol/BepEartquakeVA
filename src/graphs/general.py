import pandas as pd
import plotly.express as px
from datetime import datetime as dt

def general_graph(data, option, magrange, n_clusters):

    lon = [item['geometry']['coordinates'][0] for item in data]
    lat = [item['geometry']['coordinates'][1] for item in data]
    size = [item['properties']['sig'] for item in data]
    time = [dt.fromtimestamp(item['properties']['time']/1000) for item in data]
    mag = [item['properties']['mag'] for item in data]
    place = [item['properties']['place'] for item in data]
    sig = [item['properties']['sig'] for item in data]

    if option is None:
        return {}
    if option == 'Scatter':
        

        fig = px.scatter_mapbox(data, lat=lat, lon=lon, color=mag, range_color=[2.5, 10],
        size=size, hover_name=time,
        color_continuous_scale='viridis', size_max=10, zoom=0.6, opacity=0.6)
        
        return fig
    if option == 'Densitymap':
        fig = px.scatter_mapbox(data, lat=lat, lon=lon, color=mag, range_color=[2.5, 10],
                                    size=sig, hover_name=place,
                                    color_continuous_scale='viridis', size_max=10, zoom=0.6, opacity=0.6)
        return fig
    
    return {}