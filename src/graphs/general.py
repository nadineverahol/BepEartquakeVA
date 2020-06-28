import pandas as pd
import plotly.express as px


def general_graph(data_dict, option, min_mag, n_clusters):
    if option is None:
        return {}
    if option == 'Scatter':
        filtered_df = pd.DataFrame.from_dict(data_dict)
        fig = px.scatter_mapbox(filtered_df, lat='lat', lon='long', color='mag', range_color=[2.5, 10],
                                size='significance', hover_name='timestamp',
                                color_continuous_scale='Bluered', size_max=10, zoom=0.6, opacity=0.6)

        return fig

    return {}