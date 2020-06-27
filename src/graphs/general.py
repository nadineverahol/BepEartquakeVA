import pandas as pd
import plotly.express as px

def general_graph(data, option, min_mag, n_clusters):
    if option is None:
        return {}
    if option == 'Scatter':
        
        lon = [item['geometry']['coordinates'][0] for item in data]
        lat = [item['geometry']['coordinates'][1] for item in data]
        size = [item['properties']['sig'] for item in data]
        time = [item['properties']['time'] for item in data]

        fig = px.scatter_mapbox(data, lat=lat, lon=lon, color=[item['properties']['mag'] for item in data], range_color=[2.5, 10],
        size=size, hover_name=time,
        color_continuous_scale='Bluered', size_max=10, zoom=0.6, opacity=0.6)
        
        return fig
    if option == 'Densitymap':
        fig = px.scatter_mapbox(data, lat='lat', lon='lon', color='mag', range_color=[2.5, 10],
                                    size='sig', hover_name='place',
                                    color_continuous_scale='bluered', size_max=10, zoom=0.6, opacity=0.6)
        return fig
    
    return {}