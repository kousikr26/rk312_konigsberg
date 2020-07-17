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
filepath=Path("/home/iit/SIH/cdr-viz/data/data.csv")
df = pd.read_csv(filepath)
rows_count=len(df.index)


#Modifying the date format so date comparison becomes easy
df['Date']=df['Date'].apply(pd.to_datetime).dt.date
df['Time']=df['Time'].apply(pd.to_datetime).dt.time

for i in range(rows_count):
      df.at[i,'DateTime'] = datetime.datetime.combine(df.at[i,"Date"],df.at[i,"Time"])

#df['DateTime']=df['DateTime'] = df['DateTime'].apply(pd.to_datetime).dt.datetime

# ...............................................TEST ........................................................
#print(df.head())
#print(type(df.at[0,'DateTime']))

# ...............................................TEST ........................................................
#a=df.at[0,'DateTime']
#b=df.at[0,'Date']
#c=df.at[0,'Time']
#print(type(a))
#print(type(b))
#print(type(b))

# ...............................................TEST ........................................................
#print(df.head())
#print(df.at[670,'Date'])
#print(df.at[670,'Time'])
#print(type(df.at[670,'Date']))
#print(type(df.at[670,'Date']))


# Selecting the interval,this will be the input by the user
# Hardcoded time interval values, can be modified later
start_date="2020-06-10"
end_date="2020-06-15"
start_time="17:30:00"
end_time="19:34:52"


def date_time_format(start_date,start_time,end_date,end_time):
    Interval=dict()
    Interval['start_date'] = datetime.datetime.strptime(start_date,'%Y-%m-%d').date()
    Interval['start_time'] = datetime.datetime.strptime(start_time,'%H:%M:%S').time()
    Interval['start']=datetime.datetime.combine(Interval['start_date'],Interval['start_time'])
    Interval['end_date'] = datetime.datetime.strptime(end_date,'%Y-%m-%d').date()
    Interval['end_time'] = datetime.datetime.strptime(end_time,'%H:%M:%S').time()
    Interval['end']=datetime.datetime.combine(Interval['end_date'],Interval['end_time'])
    return Interval

# ...............................................TEST ........................................................
#Interval=date_time_format(start_date,start_time,end_date,end_time)
#print(Interval)


# Creating the Adjacency list according to the given time interval chosen by the user

# Visited denotes the vertices visited and also the discovery timestamp or distance from the source vertex
# Initializeing -1 for not discovered and storing the distance when visited/discovered
 

Interval=date_time_format(start_date,start_time,end_date,end_time)
start_interval = Interval['start']
end_interval = Interval['end']


# Using the dataframe and extracting the information for the chosen time interval
# Creating an Adjacency list for the graph


graph = defaultdict(list)
for i in range(rows_count):
    if df.at[i,'DateTime'] >= start_interval and df.at[i,'DateTime'] <= end_interval: 
        graph[df.at[i,"Caller"]].append(df.at[i,"Receiver"]) 
        graph[df.at[i,"Receiver"]].append(df.at[i,"Caller"])


unique_callers = df["Caller"].unique()
unique_receivers = df["Receiver"].unique()

visited = dict()

for i in range(unique_callers.shape[0]):
      visited[unique_callers[i]] = -1

for j in range(unique_receivers.shape[0]):
      visited[unique_receivers[j]] = -1

# ...............................................TEST ........................................................
#print(unique_callers)
#print(unique_callers.shape)
#print(visited)
#print(len(visited))
#print(unique_callers.shape)
#print(unique_callers.shape[0])
#print(type(unique_callers.shape[0]))

queue = []

# Will return all the members requested
# Either the K-distance neighbours or the entire connected component starting from that user

# This will return the entire connected component
# Returns a list of tuples for plotting
def BFS2a(df,Person1,queue,visited):
      queue.append(Person1)
      visited[Person1] = 0
      
      # Initialize the list of tuples
      final_list=[]
      while queue:
          cur_vertex=queue.pop(0)
          cur_distance = visited[cur_vertex]

          for node in graph[cur_vertex]:
              if visited[node]==-1:
                 queue.append(node)
                 # Add to a list of tuples
                 tup = (cur_vertex,node)
                 final_list.append(tup)
                 visited[node] = cur_distance+1
      return final_list

# This will return the K-distance neighbours from BFS
# Returns a list of tuples for plotting, each tuple in the list is an edge of the graph
def BFS2b(df,Person1,queue,visited,K):
      queue.append(Person1)
      visited[Person1] = 0
      
      final_list=[]
      while queue:
          cur_vertex=queue.pop(0)
          cur_distance = visited[cur_vertex]

          if cur_distance == K-1:
             break

          for node in graph[cur_vertex]:
              if visited[node]==-1:
                 queue.append(node)
                 tup = (cur_vertex,node)
                 final_list.append(tup)
                 visited[node] = cur_distance+1
      return final_list


# Checks if there is a transaction between two provided users/numbers
# Returns a boolean denoting the existence, each tuple in the list is an edge of the graph
def BFS3(df,Person1,Person2,queue,visited):
      Communicated = False
      queue.append(Person1)
      visited[Person1] = 0

      while queue:
          cur_vertex=queue.pop(0)
          if(cur_vertex==Person2):
                Communicated=True
                break
          
          cur_distance = visited[cur_vertex]
          for node in graph[cur_vertex]:
              if visited[node]==-1:
                 queue.append(node)
                 visited[node] = cur_distance+1

      return Communicated 