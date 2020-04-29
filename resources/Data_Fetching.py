import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import geopandas as gpd
# import geoplot as gplt
from shapely.geometry import Point
import plotly.graph_objects as go
import json
import urllib
import time
import requests
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


# Building df with multiple years
d = []
years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
         2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]

total = time.time()

for year in years:
    year_timer = time.time()

    # Fetching per half year because of server limitations (20k instances per query)
    half1_start = str(year) + str("-01-01")
    half1_end = str(year) + str("-06-31")
    half2_start = str(year) + str("-07-01")
    half2_end = str(year) + str("-12-31")

    # First half of the year
    r1 = requests.get(url=createUrl(half1_start, half1_end, 2.5, 100))
    data1 = r1.json()

    # Second half of the year
    r2 = requests.get(url=createUrl(half2_start, half2_end, 2.5, 100))
    data2 = r2.json()

    # Make them iterable
    data_list = [data1, data2]

    # Timing operations
    d_timer = time.time()
    for data in data_list:
        for feature in data['features']:
            d.append(
                {
                    "long": feature['geometry']['coordinates'][0],
                    'lat': feature['geometry']['coordinates'][1],
                    'mag': feature['properties']['mag'],
                    'tsunami': feature['properties']['tsunami'],
                    'significance': feature['properties']['sig'],
                    'timestamp': time.strftime('%Y/%m/%d %H:%M:%S',
                                               time.gmtime((feature['properties']['time'] / 1000.)))
                }
            )

    print("fetching data took {} seconds for period {} to {}".format(
        time.time() - year_timer, half1_start, half2_end))

df = pd.DataFrame(d)
df = df.sort_values('timestamp')
df.reset_index(inplace=True)

print("total time taken in seconds:", time.time() - total)

df.to_csv("data.csv")
