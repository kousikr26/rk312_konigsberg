import pandas as pd
from matplotlib import cm
import numpy as np

df = pd.read_csv("../data/data.csv")

#Color scale of edges
viridis = cm.get_cmap('viridis', 12)
# Define Color
df['Dura_color']=(df['Duration']/df['Duration'].max()).apply(viridis)

#Node calculation and dataframe cleaning

nodes=list(np.union1d(df['Caller'].unique(),df['Receiver'].unique()))
df['Date']=df['Date'].apply(pd.to_datetime).dt.date
df['Caller_node']=df['Caller'].apply(lambda x:list(nodes).index(x))
df['Receiver_node']=df['Receiver'].apply(lambda x:list(nodes).index(x))
