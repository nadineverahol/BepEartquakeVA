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
from graphs.clustering import clustering_graph 
from graphs.time import time_graph 
from graphs.prediction import prediction_graph 
from graphs.aftershocks import aftershocks_graph 
from graphs.tsunami import tsunami_graph 

###
# Configuration
###

df = pd.read_csv('resources/data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y/%m/%d %H:%M:%S")
px.set_mapbox_access_token("pk.eyJ1IjoidHJvdzEyIiwiYSI6ImNrOWNvOGpiajAwemozb210ZGttNXpoemUifQ.HtK_x39UnnD2_bXveR9nsQ")

tabs = ["Clustering", "Time Analysis", "Prediction", "Aftershocks", "Tsunamis"]
tab_graphs = [clustering_graph, time_graph, prediction_graph, aftershocks_graph, tsunami_graph]
tab_map_options = [
    [
        {'label': 'Scatterplot', 'value': 'Scatter'},
        {'label': 'Density map', 'value': 'Densitymap'},
        {'label': 'K-means Clustering', 'value': 'K-means-Clustering'},
        {'label': 'Agglomerative Hierarchical Clustering', 'value': 'Agglomerative'},
        {'label': 'Density based spatial clustering', 'value': 'DBSCAN'},
        {'label': 'OPTICS clustering', 'value': 'OPTICS'}
    ], 
    [
        {'label': 'Scatterplot', 'value': 'Scatter'},
        {'label': 'Density map', 'value': 'Densitymap'},
        {'label': 'K-means Clustering', 'value': 'K-means-Clustering'},
        {'label': 'Agglomerative Hierarchical Clustering', 'value': 'Agglomerative'},
    ], 
    [
        {'label': 'Scatterplot', 'value': 'Scatter'},
        {'label': 'Density map', 'value': 'Densitymap'},
        {'label': 'K-means Clustering', 'value': 'K-means-Clustering'},
    ], 
    [
        {'label': 'Scatterplot', 'value': 'Scatter'},
        {'label': 'Density map', 'value': 'Densitymap'},
    ], 
    [
        {'label': 'Scatterplot', 'value': 'Scatter'},
    ], 
]


###
# Layouts
###

def get_header():
    return html.Div(dbc.NavbarSimple(
        brand="Earthquake Visualization Tool",
        brand_href="#",
        color="primary",
        dark=True,
    ))

def get_tabs(view):
    return dbc.Tabs([dbc.Tab(label=tab, tab_id=tab) for tab in tabs],
        id="tabs",
        active_tab=view,
    )

def get_sidebar_left(view):
    content = [ 
        html.H4("Filters"),
        html.Hr(),
        
        # Time range filter
        html.P('Filter time range'),
        dcc.DatePickerRange(
            id='date-range',
            min_date_allowed=dt(2000, 1, 1),
            max_date_allowed=dt(2020, 3, 31),
            start_date=dt(2011, 1, 1).date(),
            end_date=dt(2011, 12, 31).date(),
            start_date_placeholder_text='Start Period',
            end_date_placeholder_text='End Period',
            calendar_orientation='vertical'
        ),

        # for minimum magnitude selection (if None, plot cubic 0 on map)
        html.P('Minimum magnitude'),
        dcc.Input(
            id='min-magnitude',
            type='number',
            placeholder='minimum magnitude',
            value=5,
            min=1,
            max=10,
        )
    ]

    content.append(html.Div([
        html.P('Select # clusters'),
        dcc.Input(
            id='number-of-clusters',
            type="number",
            placeholder='fill in number of clusters',
            value=25,
            min='2',
            max='100'
        )],  style={"display": "block" if view == "Clustering" else "none"}
    ))
    

    content.append(html.P('Select visualization'))
    content.append(dcc.Dropdown(
            id='main-map-selector',
            options=tab_map_options[tabs.index(view)],
            value='Scatter',
            multi=False,
            optionHeight=50,
            placeholder="Select visualization"
        ))

    content.append(dbc.Alert('Last updated: \n 26 June, 2020', color='primary'))

    return html.Div(content, style={
        "position": "sticky",
        "padding": "2rem 1rem",
        "background-color": "secondary",
    })

def get_graph(view):
    return html.Div([
        html.H4("Visualisation"),
        html.Hr(),
        dcc.Graph(id='graph', style={
            'height': "25vw",
            'width': "50vw"}
        ),
    ])

def get_sidebar_right(view):
    return html.Div([
        html.H4("Metadata"),
        html.Hr(),
        dcc.Graph(id='hist_of_mag', style={
            'height': 600,
            'width': "22vw"
        })
    ])

def bootstrap(view):
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
    app.layout = html.Div(
    [
        dcc.Store(id='storage'),
        get_header(),
        get_tabs(view),
        html.Div(
            dbc.Row(
                [
                    dbc.Col(get_sidebar_left(view), width=2, id="sidebar_left"),
                    dbc.Col(get_graph(view), width=7, id="graph_container"),
                    dbc.Col(get_sidebar_right(view), width=3, id="sidebar_right"),
                ]
            ), className="container-fluid" 
        )
    ])

    return app

app = bootstrap(tabs[0])


###
# Callbacks
###

@app.callback(
    [Output("sidebar_left", "children"),
    Output("graph_container", "children")],
    [Input("tabs", "active_tab")],
)
def tab_changed(view):
    return [get_sidebar_left(view), get_graph(view)]

@app.callback(
    Output('storage', 'data'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('min-magnitude', 'value')])
def filter_data(start_date, end_date, value):
    if value is None:
        return {}

    else:
        filtered_df = df[(df.timestamp.between(start_date, end_date)) & (df.mag >= value)]
        dic = filtered_df.to_dict()
        return dic


@app.callback(
    Output('graph', 'figure'),
    [Input('storage', 'data'),
     Input('main-map-selector', 'value'),
     Input('min-magnitude', 'value'),
     Input('number-of-clusters', 'value'), 
     Input("tabs", "active_tab")])
def update_main_graph(dic, option, min_mag, n_clusters, view):
    return tab_graphs[tabs.index(view)](dic, option, min_mag, n_clusters)


@app.callback(
    Output('hist_of_mag', 'figure'),
    [Input('storage', 'data')])
def update_side_graphs(dic):
    filtered_df = pd.DataFrame.from_dict(dic)

    if filtered_df.empty:
        return {}
    else:
        fig = make_subplots(rows=1, cols=2)
        trace0 = go.Histogram(x=filtered_df['mag'], name='Magnitudes',
                            xbins=dict(
                                start=2.5,
                                end=10,
                                size=1
                            )
                            )
        trace1 = go.Histogram(x=filtered_df['significance'], name='Significances',
                            xbins=dict(
                                start=50,
                                end=1000,
                                size=50
                            )
                            )

        fig.append_trace(trace0, 1, 1)
        fig.append_trace(trace1, 1, 2)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)