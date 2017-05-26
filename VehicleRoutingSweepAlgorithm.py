# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 22:22:03 2017

@author: Sriva
"""

import sqlite3
import math

db_connect = sqlite3.connect('database/dominos_G01004697.db')
db_handle = db_connect.cursor()

#Get the stores details that needs to be served from the bearing data       
db_handle.execute('SELECT * FROM bearingForStoresAndDC5;')
storesSupplied = db_handle.fetchall()
count = 0 #Counter for stores
i=0 #Counter for trucks          
nextTruck = True
FromDC5 = True
distanceCovered = 0
storesProcessed = 0

# List of stores data to estimate the next store serving time by a truck
db_handle.execute('SELECT StoreNumber FROM bearingForStoresAndDC5');
stores = db_handle.fetchall()
stores = list(stores)
stores = [int(k[0]) for k in stores]

#Create the table to save the truck and corresponding store it serves
db_handle.execute('CREATE TABLE IF NOT EXISTS truckRequirementDC5(Truck VARCHAR(15),StoreNumber NUMBER);')
db_handle.execute('DELETE FROM truckRequirementDC5;')
#Sweep across the stores in anticlockwise direction and determine the truck          
for row in storesSupplied:
    #print "\nProcessing Store " + str(row[0]) + " with demand " + str(row[3]) + "....."
    print "Store Number: ", count + 1
    storesProcessed = storesProcessed + 1
    pizzaDemand = row[3]
    thinCrustDemand = math.ceil(pizzaDemand * 0.15)
    regularDemand = pizzaDemand - thinCrustDemand
    
    #doughPallet demand calculation
    if regularDemand < 180:
        doughPallet = 1
        #print "Number of Dough Pallet demand is ",doughPallet
    else:
        doughPallet = math.ceil(regularDemand / 180)
        #print "Number of Dough Pallets demand are ",doughPallet
    
    #commodityPallet demand calculation - ThinCrust, Cheese and Sauce
    #thinCrustBoxes
    if thinCrustDemand <= 60:
        thinCrustBoxCount = 1
        #print "ThinCrustBoxCount is ",thinCrustBoxCount
    else:
        thinCrustBoxCount = math.ceil(thinCrustDemand/60)
        #print "ThinCrustBoxCount is ",thinCrustBoxCount
    #SauceBoxes
    sauceDemand = pizzaDemand * 0.25
    if sauceDemand <= 42:
        sauceBoxCount = 1
        #print "SauceBoxCount is ",sauceBoxCount
    else:
        sauceBoxCount = math.ceil(sauceDemand/42)
        #print "SauceBoxCount is ",sauceBoxCount
    #CheeseBoxes
    cheeseDemand = pizzaDemand * 0.75
    if cheeseDemand <= 14:
        cheeseBoxCount = 1
        #print "CheeseBoxCount is ",cheeseBoxCount
    else:
        cheeseBoxCount = math.ceil(cheeseDemand/14)
        #print "CheeseBoxCount is ",cheeseBoxCount
    #Number of stacks - Max 10 for one ingredient pallet as only the ingredients can be stacked upto 5ft
    #thinCrustStack 
    if thinCrustBoxCount <= 6:
        tcStackCount = 1
        #print "ThinCrustStackCount is ",  tcStackCount
    else:
        tcStackCount = math.ceil(thinCrustBoxCount/12)
        #print "ThinCrustStackCount is ",  tcStackCount
    #Sauce Stack Count        
    if sauceBoxCount <= 10:
        sauceStackCount = 1
        #print "SauceStackCount is ", sauceStackCount
    else:
        sauceStackCount = math.ceil(sauceBoxCount/10)
        #print "SauceStackCount is ", sauceStackCount
    #Cheese Stack Count
    if cheeseBoxCount <= 12:
        cheeseStackCount = 1
        #print "CheeseStackCount is", cheeseStackCount
    else:
        cheeseStackCount = math.ceil(cheeseBoxCount/6)
        #print "CheeseStackCount is", cheeseStackCount
    totalStacks = tcStackCount+sauceStackCount+cheeseStackCount
    #print "TotalStacks", totalStacks
    if totalStacks <= 10:
        ingredientPallet = 1
        #print "Number of Ingredient Pallet demand is ",ingredientPallet
    else:
        ingredientPallet = math.ceil(totalStacks/10)
        #print "Number of Ingredient Pallet demand is ",ingredientPallet
        
    
    #Truck Initialization
    if nextTruck == True:
        print "Truck Initialization"
        TruckName = "Truck-" + str(i)
        i = i+1
        FromDC5 = True
        totalDistanceCovered = 0
        allocatedCommodityPallets = 0
        allocatedDoughPallets = 0
        availablePalletSpace = 0
        estimatedTotalTimeBackToDC = 0
        estimatedTimeToServeNextStore = 0
        distanceCovered = 0
        nextTruck = False

    #Pallet Allocation in trucks
    palletAllocation = {0:42,1:41,2:39,3:37,4:34,5:32,6:30,7:28,8:26,9:24,10:22,11:19,12:17,13:15,14:13,15:10,16:8,17:6,18:4,19:2,20:0}
    if allocatedCommodityPallets == 0:
        allocatedCommodityPallets = ingredientPallet
    else:
        allocatedCommodityPallets = allocatedCommodityPallets + ingredientPallet
    
    if allocatedDoughPallets == 0:
        availablePalletSpace = palletAllocation.get(allocatedCommodityPallets)
    else:
        availablePalletSpace = palletAllocation.get(allocatedCommodityPallets) - allocatedDoughPallets
    if doughPallet < availablePalletSpace:
        allocatedDoughPallets = allocatedDoughPallets + doughPallet
        if FromDC5 == True:
            #print "Travelling from DC New Truck...."
            servedStore = row[0]
            distanceCovered = row[2]
            FromDC5 = False
        else:
            #print "Travelling from one store to other store..."
            #print "Capacity is available to serve this store..."
            currentStore = row[0]
            db_handle.execute('SELECT DistanceInMiles FROM roadDistanceBetweenStores WHERE OrigStore = ? AND DestStore = ?',(servedStore,currentStore))
            distance = db_handle.fetchall()
            distanceCovered = distanceCovered + distance[0][0]
            servedStore = row[0]
        nextTruck = False
    else:
        #print "Capacity is not available in..." + TruckName
        db_handle.execute('SELECT Distance FROM bearingForStoresAndDC5 WHERE StoreNumber = ?', (servedStore,))
        distance = db_handle.fetchall()
        totalDistanceCovered = distanceCovered + distance[0][0]
        #print "Total distance Covered by" + TruckName + "is ",totalDistanceCovered
        #print "Loading the next truck...."
        TruckName = "Truck-" + str(i)
        i = i+1
        print "Truck Inititalization"
        allocatedCommodityPallets = 0
        allocatedDoughPallets = 0
        availablePalletSpace = 0
        estimatedTotalTimeBackToDC = 0
        estimatedTimeToServeNextStore = 0
        distanceCovered = 0
        totalDistanceCovered = 0
        allocatedCommodityPallets = ingredientPallet
        availablePalletSpace = palletAllocation.get(allocatedCommodityPallets)
        if doughPallet < availablePalletSpace:
            allocatedDoughPallets = allocatedDoughPallets + doughPallet
        #print "Travelling from DC New Truck...."
        servedStore = row[0]
        distanceCovered = row[2]
        nextTruck = False

    #Trucking Rules    
    estimatedDistanceBackToDC = distanceCovered + row[2]
    currentStore = stores[count]
    if currentStore <> stores[len(stores)-1]:
        nextStore = stores[count+1]
    else:
        nextStore = 0
    if nextStore != 0:
        distanceToNextStore = 0
        distanceToDCFromNextStore = 0
        db_handle.execute('SELECT * FROM roadDistanceBetweenStores WHERE OrigStore = ? AND DestStore = ?',(servedStore,nextStore))
        distanceToNextStore = db_handle.fetchall()
        distanceToNextStore = distanceToNextStore[0][2]
        db_handle.execute('SELECT * FROM bearingForStoresAndDC5 WHERE StoreNumber = ?',(nextStore,))
        distanceToDCFromNextStore = db_handle.fetchall()
        distanceToDCFromNextStore = distanceToDCFromNextStore[0][2]
    
    estimatedTotalTimeBackToDC = estimatedDistanceBackToDC/45
    if nextStore != 0:
        estimatedTimeToServeNextStore = (distanceCovered + distanceToNextStore + distanceToDCFromNextStore)/45
        distanceToNextStore = 0
        distanceToDCFromNextStore = 0
    else:
        estimatedTimeToServeNextStore = 0
    if estimatedTotalTimeBackToDC <= 14:
        if (estimatedTimeToServeNextStore <= 14 and estimatedTimeToServeNextStore != 0):
            #print "Capacity and time available to Serve next store"
            totalDistanceCovered = distanceCovered
        else:
            if estimatedTimeToServeNextStore == 0:
                #print "No more stores to serve..."
                totalDistanceCovered = estimatedDistanceBackToDC
            else:
                #print "Time not available to serve next store"
                nextTruck = True
                totalDistanceCovered = estimatedDistanceBackToDC           
    else: 
        #print "Time not available to serve next store"
        nextTruck = True
        totalDistanceCovered = estimatedDistanceBackToDC
    
    #print TruckName,currentStore,totalDistanceCovered
    try:
        db_handle.execute('INSERT INTO truckRequirementDC5(Truck,StoreNumber) VALUES(?,?)',(str(TruckName), int(currentStore)))
    except:
        print "Error inserting data..."
        pass
    count = count+1    

print "\n\nSummary output Of truck requirements for DC5 using sweep algorithm:"
print "Number of stores served is", storesProcessed
print "Number of truckd needed if all the stores ares served on the same day are", i
print "Number of trucks needed if the store are served on concescutive 3 days are", math.ceil(i/3)
db_connect.commit()
db_connect.close()