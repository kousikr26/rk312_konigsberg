import pandas as pd
import numpy as np

df1 = pd.read_csv('data.csv')
df2 = pd.read_csv('ipdr_data.csv')

list_callers = df1['Caller']
list_receivers = df1['Receiver']
list_r_not_in_c = np.setdiff1d(list_receivers,list_callers)

for x in list_r_not_in_c:
    df_temp = {'Caller':x,'Receiver':0000000000,'Date':'','Time':'','Duration':'','TowerID':'','IMEI':''}
    df1 = df1.append(df_temp, ignore_index=True)

df2.rename(index=str, columns={'IMEI': 'Caller'}, inplace=True)
df2['Receiver']=20000

df=pd.merge(df1, df2, how='outer',on=['Caller'])



df.to_csv('final_data.csv')