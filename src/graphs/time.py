import plotly.graph_objects as go
from datetime import datetime as dt
import plotly.express as px

def time_graph(data, option, min_mag, n_clusters, location):
    lon = [item['geometry']['coordinates'][0] for item in data]
    lat = [item['geometry']['coordinates'][1] for item in data]
    size = [item['properties']['sig'] for item in data]
    time = [dt.fromtimestamp(item['properties']['time']/1000) for item in data]
    mag = [item['properties']['mag'] for item in data]
    place = [item['properties']['place'] for item in data]

    if option is None:
        return {}

    if option == 'Scatter-time':
        fig = px.scatter_mapbox(data, lat=lat, lon=lon, color=mag, range_color=[2.5, 10],
        size=size, hover_name=time,
        color_continuous_scale='viridis', size_max=10, zoom=1, opacity=0.6,
        animation_frame=mag)
        
        return fig

    if option == 'Magnitude-time':

        time = [item['properties']['time'] for item in data]
        mag = [item['properties']['mag'] for item in data]

        # Create figure
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(x=list(time), y=list(mag)))

        # Set title
        fig.update_layout(
            title_text="Earthquake magnitudes over time for {}".format(location)
        )

        # Add range slider
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label="1m",
                            step="month",
                            stepmode="backward"),
                        dict(count=6,
                            label="6m",
                            step="month",
                            stepmode="backward"),
                        dict(count=1,
                            label="YTD",
                            step="year",
                            stepmode="todate"),
                        dict(count=1,
                            label="1y",
                            step="year",
                            stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
        return fig

    return {}