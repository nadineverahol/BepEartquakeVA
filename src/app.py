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
from graphs.general import general_graph
from graphs.clustering import clustering_graph
from graphs.time import time_graph
from graphs.prediction import prediction_graph
from graphs.aftershocks import aftershocks_graph
from graphs.tsunami import tsunami_graph
import dns
import pymongo
import numpy as np

###
# Configuration
###

# Load static data
df = pd.read_csv('data.csv')
tsu = pd.read_csv('tsunami_groupes.csv')
run = pd.read_csv('runup.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y/%m/%d %H:%M:%S")
tsu['timestamp'] = pd.to_datetime(tsu['timestamp'], format="%Y/%m/%d")
run['timestamp'] = pd.to_datetime(run['timestamp'], format="%Y/%m/%d")

px.set_mapbox_access_token("pk.eyJ1IjoidHJvdzEyIiwiYSI6ImNrOWNvOGpiajAwemozb210ZGttNXpoemUifQ.HtK_x39UnnD2_bXveR9nsQ")

# Load mongo data


tabs = ["General", "Clustering", "Time Analysis", "Prediction", "Aftershocks", "Tsunamis"]
tab_graphs = [general_graph, clustering_graph, time_graph, prediction_graph, aftershocks_graph, tsunami_graph]
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
        {'label': 'Source', 'value': 'Scatter'},
        {'label': 'Runup', 'value': 'Runup'},
        {'label': 'Scatterplot', 'value': 'plot'},
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
        )], style={"display": "block" if view == "Clustering" else "none"}
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
        dcc.Graph(id='Runups', style={
                    'height': "25vw",
                    'width': "50vw", }
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
     Input('min-magnitude', 'value'),
     Input('tabs', 'active_tab')])
def filter_data(start_date, end_date, value, view):
    if value is None:
        return {}
    if view == 'Tsunamis':
        filtered_tsu = tsu[(tsu.timestamp.between(start_date, end_date)) & (tsu.mag >= value)]
        filtered_df = df[(df.timestamp.between(start_date, end_date)) & (df.mag >= value)]
        val = len(filtered_df) - len(filtered_tsu)
        filtered_tsu = filtered_tsu.to_dict()
        filtered_run = run[(run.timestamp.between(start_date, end_date)) & (run.mag >= value)]
        filtered_run = filtered_run.to_dict()
        return {'tsu': filtered_tsu, 'run':filtered_run, 'value': val}

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
    if min_mag is None or min_mag > df['mag'].max():
        return {}

    return tab_graphs[tabs.index(view)](dic, option, min_mag, n_clusters)


@app.callback(
    [Output('Runups', 'style'),
     Output('Runups', 'figure')],
    [Input('storage', 'data'),
     Input('main-map-selector', 'value'),
     Input('graph', 'clickData'),
     Input('tabs', 'active_tab')])
def display_click_data(dic, option, clickData, view):
    if view == 'Tsunamis':
        if (option == 'Scatter') or (option == 'Runup'):
            if clickData:
                tsu = pd.DataFrame.from_dict(dic['tsu'])
                run = pd.DataFrame.from_dict(dic['run'])
                runups = tsu[tsu['gid'] == clickData['points'][0]['customdata'][0]]
                runup = run[run['gid']== clickData['points'][0]['customdata'][0]]
                runup['runup'] = 'Runup'
                runup['Log(Height)'] = np.log(runup['Max Water Height'])

                fig=px.scatter_mapbox(runup, lat='lat', lon='long',  color= 'Log(Height)',
                                        range_color=[-5, 4], hover_name= 'runup',
                                        hover_data = ['timestamp2', 'Max Water Height', 'Distance from Source', 'long', 'lat'],
                                        size_max=10, zoom=1, opacity=0.6,
                                        color_continuous_scale='Bluered')
                fig.add_trace(px.scatter_mapbox(runups, lat='lat', lon='long', color=[5], range_color=[-4,5],
                                                hover_name=['Source'],
                                                color_continuous_scale='Bluered', size=[8], size_max=10,
                                                zoom=0, opacity=0.8).data[0])
                fig.update_layout(height=500)
                return {'height': "25vw", 'width': "50vw"}, fig

    return {'display': 'none'}, {}




@app.callback(
    [Output('hist_of_mag', 'style'),
    Output('hist_of_mag', 'figure')],
    [Input('storage', 'data'),
     Input('min-magnitude', 'value'),
     Input("tabs", "active_tab"),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')])
def update_side_graphs(dic, min_mag, view, start_date, end_date):
    filtered_df = pd.DataFrame.from_dict(dic)

    if filtered_df.empty:
        return {}
    if view == 'Tsunamis':
        tsu = pd.DataFrame.from_dict(dic['tsu'])
        fig = make_subplots(rows=3, cols=2, specs=[[{'colspan':2, 'type':'pie'}, None],
                                                   [{'b':0.07},{'b':0.07}],[{}, {}]],
                            vertical_spacing=0.006, row_heights=[0.7,1,1])
        fig.append_trace(go.Histogram(x=tsu['mag'], showlegend=False,
                                      xbins=dict(size=0.4)),2,1)
        fig.append_trace(go.Histogram(x=tsu['Focal Depth (km)'],showlegend=False,
                                      xbins=dict(size=5)),2,2)
        fig.append_trace(go.Histogram(x=np.log(tsu['Number of Runups']),showlegend=False,
                                      xbins=dict(size=1)),3,1)
        fig.append_trace(go.Histogram(x=np.log(tsu['Maximum Water Height (m)']),showlegend=False,
                                      xbins=dict(size=1)),3,2)
        fig.append_trace(go.Pie(values=[dic['value'], len(tsu)],
                     labels=["Earthquakes that didn't caused a tsunami", 'Earthquakes that did cause a tsunami'],
                     sort=False),1,1)
        fig.update_layout(legend=dict(x=0,y=1.1))
        fig.update_xaxes(title_text="Magnitude", row= 2, col= 1, title_font= {'size':10})
        fig.update_xaxes(title_text="Focal Depth (km)", row=2,col=2, title_font= {'size':10})
        fig.update_xaxes(title_text="Log(Number <br>of  Runups)", row=3,col=1, title_font= {'size':10})
        fig.update_xaxes(title_text="Log(Maximum <br>Water  Height (m))", row=3,col=2, title_font= {'size':10})
        return {'height': 800,'width': "22vw"}, fig
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

        return {'height': 600,'width': "22vw"}, fig


if __name__ == '__main__':
    app.run_server(debug=True)