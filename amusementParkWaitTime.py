# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 20:45:11 2017

@author: Sriva
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 00:29:36 2017
@author: Srivarsini
@descsription: HW01 script to scrape the disney wait times

"""
def main():

#import the required packages
    from bs4 import BeautifulSoup
    from datetime import datetime
    from collections import defaultdict
    import requests
    import csv
    import sys
    import re
    import sqlite3

#read the data from csv
    parkRides = defaultdict(list)
    with open('data/goodRides.csv') as f:
        goodRides = csv.reader(f)
        for ride in goodRides:
            for (i,v) in enumerate(ride):
                parkRides[i].append(v)
    mk = filter(None,parkRides[0]) #filter any empty item in the list of rides of magic kingdom
    ep = filter(None,parkRides[1]) #filter any empty item in the list of rides of epcot
    
#scrape the data
    interestedRideList = list()
    urlList = ['http://www.easywdw.com/waits/?&park=mk&showOther=true','http://www.easywdw.com/waits/?&park=ep&showOther=true']
    for url in urlList:
        print "\n" + url        
        if "mk" in url:
            print "Gathering Magic Kingdom Wait Times.."
            parkName = "Magic Kingdom"
            goodRides = mk
        elif "ep" in url:
            print "Gathering Epcot Wait Times.."
            parkName = "Epcot"
            goodRides = ep
        else:
            print "Something is wrong"
            sys.exit()
            
#get the content    
        scrapeTime = datetime.now().replace(microsecond=0)
        page = requests.get(url)
        soup = BeautifulSoup(page.content)
        table = soup.find('table')
        rideData = table.findAll('tr')
        rideCount = 0
        print "\n"
        for ride in rideData:
            interestedRides = list()
            rideInfo = ride.findAll('td')
            
            try:
                if rideInfo[0].getText() in str(goodRides):
                    rideCount = rideCount + 1
                    interestedRideName = str(rideInfo[0].getText())
                    interestedRideLocation = str(rideInfo[1].getText())
                    interestedRideWaitTime = re.sub("\D","",str(rideInfo[2].getText()))
                    if interestedRideWaitTime:
                        interestedRides.append(parkName)
                        interestedRides.append(scrapeTime)
                        interestedRides.append(interestedRideName)
                        interestedRides.append(interestedRideLocation)
                        interestedRides.append(interestedRideWaitTime)
                        interestedRideList.append(interestedRides)
                    if parkName is "Magic Kingdom" and interestedRideWaitTime:
                        print rideCount, interestedRideName + "------" + interestedRideLocation + "------" + interestedRideWaitTime + " Minutes"
                    elif parkName is "Epcot":
                        if rideCount == 1:
                            print "Selected 15 Epcot Rides based on thrill level and interests. Below are the selected rides,\n"
                        print rideCount,interestedRideName
                    else:
                        print rideCount, interestedRideName + "---- No Wait time"            
            except:
                pass
                               
#connect to sqlite database and get the connection object
    db_connect = sqlite3.connect('database/disney_G01004697.db')
    db_connect.execute("CREATE TABLE IF NOT EXISTS DISNEY (ParkName TEXT  NOT NULL,ScrapeDate DATE, RideName TEXT NOT NULL, Location TEXT, WaitTimeInMinutes INTEGER);")
    db_handle = db_connect.cursor()
    
#insert the rides into database
    try:
        for items in interestedRideList:
            db_handle.execute('INSERT INTO DISNEY(ParkName,ScrapeDate,RideName,Location,WaitTimeInMinutes) values(?,?,?,?,?)',(items[0],items[1],items[2],items[3],items[4]))
    except:
        pass   
    db_connect.commit()
    db_connect.close()
#End of main function
    
# Call to main function
if __name__ == "__main__":
    main()
#End of call
    
#End of script