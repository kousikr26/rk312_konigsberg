<<<<<<< HEAD
import pandas as pd
def meanDur(nodeNumber,df):
    #print(df['Caller_node'].unique(),df['Receiver_node'].unique(),nodeNumber)
    return df[(df['Caller_node'] == nodeNumber) | (df['Receiver_node'] == nodeNumber) ]['Duration'].mean()

#returns a dictionary with the number of minutes of talk
#time corresponding to each hour of the day
#Note that m[i] corresponds to the total minutes of talk
#time from ith hour to (i+1)th hour
def peakHours(nodeNumber,df):
    m = {}
    for i in range(24):
        m[i] = 0
    df1 = df[(df['Caller_node'] == nodeNumber) | (df['Receiver_node'] == nodeNumber) ]
    for i in list(df1.index):
        h = int(df1.at[i,'Time'][0:2])
        min = int(df1.at[i,'Time'][3:5])
        dur = df1.at[i,'Duration']
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
    m={k: v for k, v in sorted(m.items(), key=lambda item: item[1], reverse=True)}
    i = 0
    n = {}
    for x in m:
        if i<3:
            n[x]=m[x]
            i+=1
        else:
            break
    return n

#returns a list of size 2
#first element -> no. of outgoing calls
#second element -> no. of incomming calls
def ogIc(x,df):
    z = [0,0]
    z[0] = len(df[df['Caller_node'] == x])
    z[1] = len(df[df['Receiver_node'] == x])
    return z

#returns a list of size 3
#first element -> most calls to
#second element -> most calls from
#third element -> most calls in total
def mostCalls(nodeNumber,df):
    m1 = {}
    m2 = {}
    m3 = {}
    df1 = df[(df['Caller_node'] == nodeNumber) | (df['Receiver_node'] == nodeNumber) ]
    for i in list(df1.index):
        if df1.at[i,'Caller_node'] == nodeNumber:
            if df1.at[i,'Receiver'] in m1:
                m1[df1.at[i,'Receiver']]+=1
                m3[df1.at[i,'Receiver']]+=1
            else:
                m1[df1.at[i,'Receiver']]=1
                m3[df1.at[i,'Receiver']]=1
        elif df1.at[i,'Receiver_node'] == nodeNumber:
            if df1.at[i,'Caller'] in m2:
                m2[df1.at[i,'Caller']]+=1
                m3[df1.at[i,'Caller']]+=1
            else:
                m2[df1.at[i,'Caller']]=1
                m3[df1.at[i,'Caller']]=1
    z = []
    if not not m1:
        z.append(max(m1, key=m1.get))
    else:
        z.append("None")
    if not not m2:
        z.append(max(m2, key=m2.get))
    else:
        z.append("None")
    if not not m3:
        z.append(max(m3, key=m3.get))
    else:
        z.append("None")

    return z

=======
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
print(df.head())
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





def ogIc(x):
    z = [0,0]
    for i in range(rows_count):
        if df.at[i,'Caller'] == x:
            z[0]+=1
        elif df.at[i,'Receiver'] == x:
            z[1]+=1
    return z

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

print(meanDurationOfCalls(7978131764))
key_value = (peakHours(7978131764))
print( sorted(key_value.items(), key = lambda kv:(kv[1], kv[0])) )

print(" ")
print (ogIc(7978131764))
print(mostCalls(7978131764))
>>>>>>> added BFS.py and stats.py
