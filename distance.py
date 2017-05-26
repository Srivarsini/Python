# -*- coding: utf-8 -*-
"""
Created on Mon Feb 06 18:04:32 2017

@author: Sriva
"""

from haversine import haversine
from collections import defaultdict
import sqlite3
import keysAndLists as kl
import urllib, json
import time

#Question 2: Obtain the details of stores within 100 miles for each store in NY

#Connect to database to retrieve the store details in NewYork
start_time = time.time()
db_connect = sqlite3.connect('database/McDonalds_G01004697.db')
db_handle = db_connect.cursor()
db_handle.execute('select OriginStoreNumber,OriginCity, OriginState,OriginLatitude,OriginLongitude,DestStoreNumber,DestCity,DestState,DestLatitude,DestLongitude from (select a.StoreNumber as OriginStoreNumber, a.city as OriginCity, a.state OriginState, a.latitude as OriginLatitude,a.longitude as OriginLongitude,b.StoreNumber as DestStoreNumber, b.city as DestCity,b.State as DestState,b.latitude as DestLatitude,b.longitude as DestLongitude,(a.latitude-b.latitude) As latDifference, (a.longitude-b.longitude) as lngDifference from McDonalds a join McDonalds b where latDifference between -1.44 and 1.44 and lngDifference between -1.66 and 1.66) where OriginState like \'%NY%\'')
all_rows = db_handle.fetchall()
count = 0

#Create a table for stores within 100 miles from each store in NewYork
db_handle.execute('CREATE TABLE IF NOT EXISTS StoresWithin100MilesNY(OriginStoreNumber NUMBER NOT NULL,OriginCity Varchar(30),OriginState Varchar(10), OriginLatitude UNSIGNEDINT(10), OriginLongitude UNSIGNEDINT(10), DestStoreNumber NUMBER NOT NULL, DestCity varchar(10), DestState varchar(10), DestLatitude UNSIGNEDINT(10), DestLongitude UNSIGNEDINT(10), StraightLineDistanceInMiles REAL);')
db_handle.execute('DELETE FROM StoresWithin100MilesNY;')
print "Deleted all the existing rows in StoresWithin100MilesNY"
print "Adding the data in StoresWithin100MilesNY"
for r in all_rows:
        count = count + 1
        origLatLng = r[3:5]
        destLatLng = r[8:10]
        straightlinedistance = haversine(origLatLng,destLatLng,miles = True)
        if (straightlinedistance != 0.0) and (straightlinedistance <= 100):
            db_handle.execute('insert into StoresWithin100MilesNY(OriginStoreNumber,OriginCity,OriginState,OriginLatitude,OriginLongitude,DestStoreNumber,DestCity,DestState,DestLatitude,DestLongitude,StraightLineDistanceInMiles) values(?,?,?,?,?,?,?,?,?,?,?)',(r[0],str(r[1]),str(r[2]),r[3],r[4],r[5],str(r[6]),str(r[7]),r[8],r[9],straightlinedistance));
print "No of rows processed = ", count 


#Question 3: Show the first 10 closest stores from Stores - '665596','34261','643850'
db_handle.execute('select * from (Select * FROM storesWithin100MilesNY WHERE OriginStoreNumber = 665596 order by straightlinedistanceinmiles limit 10) union select * from (Select * FROM storesWithin100MilesNY WHERE OriginStoreNumber = 34261 order by straightlinedistanceinmiles limit 10) union select * from (Select * FROM storesWithin100MilesNY WHERE OriginStoreNumber = 643850 order by straightlinedistanceinmiles limit 10)')
all_rows = db_handle.fetchall()
city1 = list()
city2 = list()
city3= list()
destList1 = list()
destList2 = list()
destList3 = list()
destList1Formatted = list()
destList2Formatted = list()
destList3Formatted = list()
i=0
for row in all_rows:
    if row[0] == 34261:
        city1.append(row)
        origin1 = str(row[3]) + ',' + str(row[4])
        if destList1 is None:
            latlng = str(row[8]) + ',' +str(row[9])
            destList1 = destList1.append(latlng)
        else:
            latlng = str(row[8]) + ',' +str(row[9])
            destList1.append(latlng)
    if row[0] == 643850:
        city2.append(row)
        origin2 = str(row[3]) + ',' + str(row[4])
        if destList2 is None:
            latlng = str(row[8]) + ',' +str(row[9])
            destList2 = destList2.append(latlng)
        else:
            latlng = str(row[8]) + ',' +str(row[9])
            destList2.append(latlng)
    if row[0] == 665596:
        city3.append(row)
        origin3 = str(row[3]) + ',' + str(row[4])
        if destList3 is None:
            latlng = str(row[8]) + ',' +str(row[9])
            destList3 = destList3.append(latlng)
        else:
            latlng = str(row[8]) + ',' +str(row[9])
            destList3.append(latlng)
destList1Formatted = "|".join(destList1)
destList2Formatted = "|".join(destList2)
destList3Formatted = "|".join(destList3)
                  
if destList1Formatted is not None:
    url1 = 'https://maps.googleapis.com/maps/api/distancematrix/json?mode=driving&units=imperial&origins=%s&destinations=%s&key=%s'% (origin1,destList1Formatted,kl.distanceMatrix_api_key)
if destList2Formatted is not None:
    url2 = 'https://maps.googleapis.com/maps/api/distancematrix/json?mode=driving&units=imperial&origins=%s&destinations=%s&key=%s'% (origin2,destList2Formatted,kl.distanceMatrix_api_key)
if destList3Formatted is not None:
    url3 = 'https://maps.googleapis.com/maps/api/distancematrix/json?mode=driving&units=imperial&origins=%s&destinations=%s&key=%s'% (origin3,destList3Formatted,kl.distanceMatrix_api_key)
k=0
miles = defaultdict(list)
for url in [url1,url2,url3]:
    result= json.load(urllib.urlopen(url))
    rd = list()
    for rs in result['rows'][0]['elements']:
        if rd is None:
            rd = rs['distance']['text']
        else:
            rd.append(rs['distance']['text'])
    rd = [str(x) for x in rd]
    miles[k].append(rd)
    k=k+1
    
print "\nStores close to store number - 34261 - Aurburn - NY - Details \n"
print "Origin Store Number - Origin City - Origin State - Dest Store Number - Dest City - Dest State - St. Distance - Road Distance"
for x,y in zip(city1,miles[0][0]):
    print x[0], str(x[1]),str(x[2]),x[5],x[6],x[7],x[10],str("------") , y
print "\nStores close to store number - 643850 - Canton - NY - Details \n"
print "Origin Store Number - Origin City - Origin State - Dest Store Number - Dest City - Dest State - St. Distance - Road Distance"
for x,y in zip(city2,miles[1][0]):
    print x[0], str(x[1]),str(x[2]),x[5],x[6],x[7],x[10], str("-------"),y
print "\nStores close to store number - 665596 - Adams - NY - Details \n"
print "Origin Store Number - Origin City - Origin State - Dest Store Number - Dest City - Dest State - St. Distance - Road Distance"
for x,y in zip(city3,miles[2][0]):
    print x[0], str(x[1]),str(x[2]),x[5],x[6],x[7],x[10], str("--------"),y
    
db_connect.commit()
db_connect.close()
print "\n\nExecution time is ", time.time() - start_time