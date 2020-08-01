import pandas as pd
def meanDur(nodeNumber,df):
    #print(df['Caller_node'].unique(),df['Receiver_node'].unique(),nodeNumber)
    return df[(df['Receiver_node']!=-1)&((df['Caller_node'] == nodeNumber) | (df['Receiver_node'] == nodeNumber)) ]['Duration'].mean()

#returns a dictionary with the number of minutes of talk
#time corresponding to each hour of the day
#Note that m[i] corresponds to the total minutes of talk
#time from ith hour to (i+1)th hour
def peakHours(nodeNumber,df):
    m = {}
    for i in range(24):
        m[i] = 0
    df1 = df[(df['Receiver_node']!=-1)&((df['Caller_node'] == nodeNumber) | (df['Receiver_node'] == nodeNumber)) ]
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
    df1 = df[(df['Receiver_node']!=-1)&((df['Caller_node'] == nodeNumber) | (df['Receiver_node'] == nodeNumber)) ]
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

