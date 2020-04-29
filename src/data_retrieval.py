''' This module retrieves the data from the usgs serves and stores it in monodb. It updated the data every time it runs.'''

import requests
import pymongo
from datetime import datetime, timedelta

# Connect to the db
mongo = pymongo.MongoClient("mongodb://localhost:32768/")
collection = mongo["map-earthquake-data"]["earthquakes"]

# Select the date to start from
latest_event = collection.find_one({}, sort=[("properties.time", pymongo.DESCENDING)])
if latest_event is not None:
    start_datetime = datetime.fromtimestamp(latest_event["properties"]["time"] / 1000)
else:
    start_datetime = datetime.strptime("January 1, 2000", "%B %d, %Y")

while True: 
    # set the end_datetime
    end_datetime = start_datetime + timedelta(days=30)  
    month_iteration = 0

    print "Searching for earthquakes from",start_datetime.strftime("%Y-%m-%d"),"to",end_datetime.strftime("%Y-%m-%d")

    while True:
        # Build the url
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        url += "?format=geojson"
        url += "&orderby=time-asc"
        url += "&limit=20000"
        url += "&offset=" + str(month_iteration * 20000 + 1)
        url += "&starttime=" + start_datetime.strftime("%Y-%m-%d")
        url += "&endtime=" + end_datetime.strftime("%Y-%m-%d")

        # Retrieve the corresponding earthquakes
        response = requests.get(url)
        json = response.json()
        events = json["features"]
        
        print "Found",len(events),"earthquakes"

        # Insert all found events
        collection.insert_many(events)

        # Reiterate the month if we found more than 20k, continue with the next otherwise
        if len(events) >= 20000:
            month_iteration += 1
            print "Searching for more iterations in the current month"
        else:
            start_datetime = end_datetime
            break
    
    # Stop searching if we surpassed the current date
    if start_datetime > datetime.now():
        break


print "The earthquake register has been updated!"