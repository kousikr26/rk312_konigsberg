import pandas as pd
import numpy as np

df1 = pd.read_csv('data/data.csv')
df2 = pd.read_csv('data/ipdr_data.csv')


df2.rename(index=str, columns={'IMEI': 'Caller','Start Date':'Date','Start Time':'Time'}, inplace=True)
df2['Receiver']=20000

frames=[df1,df2]
df=pd.concat(frames)



df.to_csv('final_data.csv')