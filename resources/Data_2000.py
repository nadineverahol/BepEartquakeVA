import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import geopandas as gpd
import geoplot as gplt
from shapely.geometry import Point
import plotly.graph_objects as go
import json, urllib, time, requests
import dash

def createUrl(starttime, endtime, minmagnitude, maxdepth):
    """
    input types: str, str, int, int
    dates format: yyyy-mm-dd
    """
    st = "&starttime=" + starttime
    et = "&endtime=" + endtime
    mm = "&minmagnitude=" + str(minmagnitude)
    md = "&maxdepth=" + str(maxdepth)
    return "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson" + str(st) + str(et) + mm + md


start = time.time()
r = requests.get(url=createUrl("2000-01-01", "2000-12-31", 2.5, 100))
dataRAW = r.json()

print('fetched', len(dataRAW['features']), 'earthquakes')
print("took", time.time() - start, 'seconds')

# Manipulating data from query to make it workable in dataframe
start = time.time()

data = dataRAW['features']

long = []
lat = []
mags = []
tsunami = []
significance = []
timestamp = []
for feature in data:
    mags.append(feature['properties']['mag'])
    tsunami.append(feature['properties']['tsunami'])
    significance.append(feature['properties']['sig'])
    timestamp.append(time.strftime('%Y/%m/%d %H:%M:%S',  time.gmtime((feature['properties']['time']/1000.)))),
    long.append(feature['geometry']['coordinates'][0]),
    lat.append(feature['geometry']['coordinates'][1])



# Creating dataframe
df = pd.DataFrame(
    {'long': long,
     'lat': lat,
     'mag': mags,
     'tsunami': tsunami,
     'significance': significance,
     'timestamp' : timestamp

     })

print("Creating dataframe took", time.time() - start, 'seconds')

df.to_csv("year_2000.csv")
