import numpy as np
import pandas as pd
import os
import csv
import time
import datetime
import calendar
from datetime import datetime as dt
from pathlib import Path
from collections import defaultdict


# Reading the csv into a Pandas dataframe df

df = pd.read_csv("data.csv")
rows_count=len(df.index)

#returns the mean duration of calls
def meanDurationOfCalls(x):
    r = 0
    t = 0
    j = 0
    for i in range(rows_count):
        if df.at[i,'Caller'] == x or df.at[i,'Receiver'] == x:
            t = df.at[i,'Duration']/(j+1)
            r = r * j
            r = r / (j+1)
            r = r + t
            j = j + 1
    return r

#returns a dictionary with the number of minutes of talk
#time corresponding to each hour of the day
#Note that m[i] corresponds to the total minutes of talk
#time from ith hour to (i+1)th hour
def peakHours(x):
    m = {}
    for i in range(24):
        m[i]=0
    for i in range(rows_count):
        if df.at[i,'Caller'] == x or df.at[i,'Receiver'] == x:
            h = int(df.at[i,'Time'][0:2])
            min = int(df.at[i,'Time'][3:5])
            dur = df.at[i,'Duration']
            min = 60-min
            if(dur>min):
                 m[h]+=min
            else:
                 m[h]+=dur
            dur -= min
            while(dur>0):
                h = (h + 1)%24
                if(dur>60):
                    m[h]+=60
                    dur-=60
                else:
                    m[h]+=dur
                    dur = 0
    return (m)




#returns a list of size 2
#first element -> no. of outgoing calls
#second element -> no. of incomming calls
def ogIc(x):
    z = [0,0]
    for i in range(rows_count):
        if df.at[i,'Caller'] == x:
            z[0]+=1
        elif df.at[i,'Receiver'] == x:
            z[1]+=1
    return z

#returns a list of size 3
#first element -> most calls to
#second element -> most calls from
#third element -> most calls in total
def mostCalls(x):
    m1 = {}
    m2 = {}
    m3 = {}
    for i in range(rows_count):
        if df.at[i,'Caller'] == x:
            if df.at[i,'Receiver'] in m1:
                m1[df.at[i,'Receiver']]+=1
                m3[df.at[i,'Receiver']]+=1
            else:
                m1[df.at[i,'Receiver']]=1
                m3[df.at[i,'Receiver']]=1
        elif df.at[i,'Receiver'] == x:
            if df.at[i,'Caller'] in m2:
                m2[df.at[i,'Caller']]+=1
                m3[df.at[i,'Caller']]+=1
            else:
                m2[df.at[i,'Caller']]=1
                m3[df.at[i,'Caller']]=1
    z = [max(m1, key=m1.get),max(m2, key=m2.get),max(m3, key=m3.get)]
    return z
