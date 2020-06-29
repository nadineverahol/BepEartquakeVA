import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from datetime import datetime as dt
import pandas as pd
import geopandas
import plotly.express as px
from plotly import graph_objects as go
from matplotlib.pyplot import figure
from plotly.subplots import make_subplots

from graphs.general import general_graph
from graphs.clustering import clustering_graph 
from graphs.time import time_graph 
from graphs.prediction import prediction_graph 
from graphs.aftershocks import aftershocks_graph 
from graphs.tsunami import tsunami_graph 

from pymongo import MongoClient

###
# Configuration
###

# Connect to database
connection = MongoClient("mongodb://localhost:27017/")
db = connection["map-earthquake-data"]
collection = db.earthquakes

# Set mapbox
px.set_mapbox_access_token("pk.eyJ1IjoidHJvdzEyIiwiYSI6ImNrOWNvOGpiajAwemozb210ZGttNXpoemUifQ.HtK_x39UnnD2_bXveR9nsQ")

# Define tabs
tabs = ["General", "Clustering", "Time Analysis", "Prediction", "Aftershocks", "Tsunamis"]
tab_graphs = [general_graph, clustering_graph, time_graph, prediction_graph, aftershocks_graph, tsunami_graph]
tab_map_options = [
    [ # Main visualizations: scatter, density & parallel coordinates
        {'label': 'Scatterplot', 'value': 'Scatter'},
        {'label': 'Density map', 'value': 'Densitymap'},
        {'label': 'Parallel coordinates', 'value': 'ParallelCoordinates'},
    ], 
    [ # All clustering options
        {'label': 'K-means Clustering', 'value': 'K-means-Clustering'},
        {'label': 'Agglomerative Hierarchical Clustering', 'value': 'Agglomerative'},
        {'label': 'Density based spatial clustering', 'value': 'DBSCAN'},
        {'label': 'OPTICS clustering', 'value': 'OPTICS'}
    ], 
    [ # Time analyses
        {'label': 'Magnitude over time', 'value': 'Magnitude-time'},
        {'label': 'Scatterplot over time', 'value': 'Scatter-time'}
    ], 
    [ # Prediction analyses
        {'label': 'Line plot', 'value': 'Line'}, # Only line plot
    ], 
    [ # Aftershock analyses
        {'label': 'Scatterplot over time', 'value': 'Scatter-time'},
        {'label': 'Scatterplot', 'value': 'Scatter'},
        {'label': 'Density map', 'value': 'Densitymap'},
    ], 
    [ # To be filled by Jeroen
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
        html.P('Start date'),
        dcc.DatePickerSingle(
            id='start-date',
            min_date_allowed=dt(2000, 1, 1),
            max_date_allowed=dt(2020, 5, 30),
            initial_visible_month=dt(2011, 12, 31),
            date="2011-03-01"
        ),
        html.P('End date'),
        dcc.DatePickerSingle(
            id='end-date',
            min_date_allowed=dt(2000, 1, 1),
            max_date_allowed=dt(2020, 5, 30),
            initial_visible_month=dt(2012, 12, 30),
            date="2011-04-30"
        ),

        # Magnitude range selection
        html.P('Magnitude range'),
        dcc.RangeSlider(
            id="magnitude-range",
            min=2.5,
            max=10,
            step=0.5,
            allowCross=False,
            marks={i: '{}'.format(i) for i in range(2,10)},
            value=[2, 10],
        ),

        # Depth range selection
        html.P("Depth range"),
        dcc.RangeSlider(
            id='depth-range',
            min=0,
            max=735.8,
            step=20,
            marks={i: "{}".format(i) for i in range(0,740) if i % 100 == 0},
            value=[0, 300]
        ),        
    ]

    # Color scale selection (optional)
    content.append(html.Div([
        html.P("Select Color Scale"),
        dcc.Dropdown(
            id='color-scale',
            value='Viridis',
            options=[
                {"label": "Viridis", 'value': 'Viridis'},
                {"label": "Plasma", 'value': 'Plasma'},
                {"label": "Deep", 'value': 'Deep'},
                {"label": "Cividis", 'value': 'Cividis'}
            ]
        )
    ], style={'display': "block" if view in ["General","Time Analysis", "Aftershocks", "Tsunamis"] else 'none'}
    ))

    # Cluster selection (optional)
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

    # Location selection (optional)
    content.append(html.Div([
        html.P('Select location'),
        dcc.Dropdown(
            id='location-selector',
            placeholder='Select location',
            options=[
                {'label': 'California', 'value': 'california'},
                {'label': 'Japan', 'value': 'japan'},
                {'label': 'Italy', 'value': 'italy'},
            ]
        )],  style={"display": "block" if view in ["Time Analysis", "Aftershocks"] else "none"}
    ))

    # Visualization selection
    content.append(html.P('Select visualization'))
    content.append(dcc.Dropdown(
            id='main-map-selector',
            options=tab_map_options[tabs.index(view)],
            value='Scatter',
            multi=False,
            optionHeight=50,
            placeholder="Select visualization"
        ))

    # BEP information tag
    content.append(dbc.Card(
        dbc.CardBody(
            [
                html.H6("Last updated: " + dt.now().strftime('%d %B %Y'), className="card-subtitle"),
                # html.P(
                #     "This visualization tool is developed as part of the Bachelor End Project 2020. Contributors: Wessel Kren, Nadine Hol, Jeroen Gommers.",
                #     className="card-text",
                # ),
            ]
        ),
        style={"margin-top":"2rem"},
    ))

    return html.Div(content, style={
        "position": "sticky",
        "padding": "2rem 1rem",
        "background-color": "secondary",
    })

def get_graph(view):
    return html.Div([
        html.H4("Visualization"),
        html.Hr(),
        dcc.Graph(id='graph', style={
            'height': "32vw",
            'width': "58vw"}
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
    [Input('start-date', 'date'),
     Input('end-date', 'date'),
     Input('magnitude-range', 'value'),
     Input('depth-range', 'value'),
     Input('location-selector', 'value')])
def filter_data(start_date, end_date, mag_range, depth_range, location):
    if None in [mag_range, depth_range, start_date, end_date]:
        return {}
    
    start_date = dt.strptime(start_date, '%Y-%m-%d').timestamp() * 1000
    end_date = dt.strptime(end_date, '%Y-%m-%d').timestamp() * 1000

    query = {
        "properties.mag" : {"$gte": mag_range[0], "$lte": mag_range[1]},
        "properties.time": {"$gte":start_date, "$lte": end_date},
        "geometry.coordinates.2": {"$gte": depth_range[0], "$lte": depth_range[1]},
    }

    if location is not None:
        query["properties.place"] = {"$regex": location, '$options': 'gi'}

    print (query)

    earthquakes = list(collection.find(query, {'_id': False}).limit(5000))

    return earthquakes

@app.callback(
    Output('graph', 'figure'),
    [Input('storage', 'data'),
     Input('main-map-selector', 'value'),
     Input('magnitude-range', 'value'),
     Input('number-of-clusters', 'value'),
     Input('color-scale', 'value'),
     Input("tabs", "active_tab"),
     Input("location-selector", "value")])
def update_main_graph(dic, option, mag_range, n_clusters, colorscale, view, location):
    return tab_graphs[tabs.index(view)](dic, option, mag_range, n_clusters, colorscale, location)


@app.callback(
    Output('hist_of_mag', 'figure'),
    [Input('storage', 'data'),
    Input('graph', 'selectedData')])
def update_side_graphs(earthquakes, temp):
    if not temp:
        fig = make_subplots(rows=1, cols=2)
        trace0 = go.Histogram(x=[item['properties']['mag'] for item in earthquakes], name='Magnitudes',
                              xbins=dict(
                                  start=2.5,
                                  end=10,
                                  size=1
                              )
                              )
        trace1 = go.Histogram(x=[item['geometry']['coordinates'][2] * -1 for item in earthquakes], name='Depth distribution',
                              xbins=dict(
                                  start=-800,
                                  end=0,
                                  size=50
                              )
                              )

        fig.append_trace(trace0, 1, 1)
        fig.append_trace(trace1, 1, 2)
        fig.update_layout(legend=dict(x=0.5, y=1.2))

        return fig

    else:
        mag = [list(item.values())[7] for item in temp['points']]
        depth = [list(item.values())[8][0] * -1 for item in temp['points']]

        fig = make_subplots(rows=1, cols=2)
        trace0 = go.Histogram(x=mag, name='Magnitude distribution',
                              xbins=dict(
                                  start=2.5,
                                  end=10,
                                  size=0.5
                              )
                              )
        trace1 = go.Histogram(x=depth, name='Depth distribution',
                              xbins=dict(
                                  start=-800,
                                  end=0,
                                  size=25
                              )
                              )

        fig.append_trace(trace0, 1, 1)
        fig.append_trace(trace1, 1, 2)
        fig.update_layout(legend=dict(x=0.5, y=1.2))

        return fig

if __name__ == '__main__':
    app.run_server(debug=True)