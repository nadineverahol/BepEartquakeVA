import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import datetime as dt
import pandas as pd
import plotly.express as px
from plotly import graph_objects as go
from matplotlib.pyplot import figure
from plotly.subplots import make_subplots
import dns
import pymongo
import numpy as np


def tsunami_graph(data_dict, option, min_mag, n_clusters):
    if option is None:
        return {}
    if option == 'Scatter':
        tsu = pd.DataFrame.from_dict(data_dict['tsu'])
        tsu['Log(Number of Runups)'] = np.log(tsu['Number of Runups'])
        fig = px.scatter_mapbox(tsu, lat='lat', lon='long', color='mag', range_color=[2.5,10],
                            hover_name='timestamp2', size='Log(Number of Runups)',
                            hover_data= ['Number of Runups', 'Focal Depth (km)', 'Maximum Water Height (m)'],
                            color_continuous_scale='Bluered', size_max=10, zoom=0.1, opacity=0.6,
                            custom_data=['gid'])
        fig.update_layout(clickmode= 'event+select', height=400)
        return fig
    if option == 'Runup':
        tsu = pd.DataFrame.from_dict(data_dict['run'])
        tsu['Log(Max Water Height)'] = np.log(tsu['Max Water Height'])
        fig = px.scatter_mapbox(tsu, lat='lat', lon='long', color='Log(Max Water Height)',
                                range_color=[-5, 4], hover_name='timestamp2',
                                hover_data = ['Max Water Height', 'Distance from Source', 'long', 'lat'],
                                color_continuous_scale='Bluered', size_max=10, zoom=0.1, opacity=0.6,
                                custom_data=['gid'])
        fig.update_layout(clickmode='event+select', height = 400)
        return fig
    if option == 'plot':
        tsu = pd.read_csv('tsunami_groupes.csv')
        tsu['Log(Number of Runups)'] = np.log(tsu['Number of Runups'])
        tsu['Log(Maximum Water Height (m)'] = ((np.log(tsu['Maximum Water Height (m)'])) - (
            np.log(tsu['Maximum Water Height (m)'])).min()) / ((np.log(
            tsu['Maximum Water Height (m)'])).max() - (np.log(
            tsu['Maximum Water Height (m)'])).min())
        fig = px.scatter(tsu[~tsu['Maximum Water Height (m)'].isnull()], x='mag', y='Log(Number of Runups)', color='Max Distance',
                         size= 'Log(Maximum Water Height (m)', size_max= 8, color_continuous_scale='Bluered')
        return fig
