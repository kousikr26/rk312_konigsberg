from collections import defaultdict
import pandas as pd
def BFS4(cur_number, queue,df,visited,graph):
    queue.append(cur_number)
    visited[cur_number] = 0

    # Initialize the list of tuples(component reachable from this number)
    this_comp = set()
    while queue:
        cur_vertex = queue.pop(0)
        cur_distance = visited[cur_vertex]

        for node in graph[cur_vertex]:
            if node not in visited:
                queue.append(node)
                # Add to a this component
              #  tup = (cur_vertex, node) # what is tup doing?
                this_comp.add(node)
                this_comp.add(cur_vertex)
                visited[node] = cur_distance + 1
    return this_comp,visited


## Using the BFS4 function and finding all components
def bfs(numbers,df):
    queue = []
    visited = {}
    graph = defaultdict(list)
    #if df.at[i,'DateTime'] >= start_interval and df.at[i,'DateTime'] <= end_interval:
    df.apply(lambda x:graph[x['Caller']].append(x['Receiver']),axis=1)
    df.apply(lambda x:graph[x['Receiver']].append(x['Caller']),axis=1)
    unique_callers = df["Caller"].unique()
    unique_receivers = df["Receiver"].unique()
    numbers_status = {numbers[i]: False for i in range(len(numbers))}
    list_of_components = []
    for it in range(len(numbers_status)):
        if numbers_status[numbers[it]] == False:
            numbers_status[numbers[it]] = True
            cur_component,visited = BFS4( numbers[it], queue,df,visited,graph)
            list_of_components.append(cur_component)
    return list_of_components
