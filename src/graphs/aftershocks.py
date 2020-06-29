import plotly.graph_objects as go
from datetime import datetime as dt
import plotly.express as px

def aftershocks_graph(data, option, min_mag, n_clusters, location):
    lon = [item['geometry']['coordinates'][0] for item in data]
    lat = [item['geometry']['coordinates'][1] for item in data]
    size = [item['properties']['sig'] for item in data]
    time = [dt.fromtimestamp(item['properties']['time']/1000) for item in data]
    mag = [item['properties']['mag'] for item in data]
    place = [item['properties']['place'] for item in data]
    hours = [str(time[i].hour) + "-" + str(time[i].day) for i in range(len(time))]

    if option is None:
        return {}

    if option == 'Scatter-time':
        fig = px.scatter_mapbox(data, lat=lat, lon=lon, color=mag, range_color=[2.5, 10],
        size=size, hover_name=time,
        color_continuous_scale='viridis', size_max=10, zoom=1, opacity=0.6,
        animation_frame=hours)
        
        return fig

    return {}