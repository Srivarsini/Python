# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 22:35:01 2017

@author: Srivarsini
"""

import schedule
import time

def job():
    print("Adding the rides having wait times into disney database ...")
    execfile("disneyWaitTimeScript.py")

schedule.every(15).minutes.do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)

