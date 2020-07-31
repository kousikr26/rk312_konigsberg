import pandas as pd
df=pd.read_csv('404.csv')
#w 23.288657,77.253617
#e 23.290549,77.567319
# n 23.340995
# s 23.138466
# for i in df:
#     if(i.lat<=23.340995 and i.lat<=23.138466):
#         if(i.lon>=77.253617 and i.lon<=77.567319):
#             print(i)
towers=df[(df["lat"]<=23.340995) & (df["lat"]>=23.138466) & (df["lon"]<=77.567319) & (df["lon"]>=77.253617)]
towers['TowerID']=towers['mcc'].apply(str)+towers['net'].apply(str)+'-'+towers['area'].apply(str)+'-'+towers['cell'].apply(str)
towers.drop(['created','updated','averageSignal','samples','changeable','mcc','net','area','unit','cell'],axis=1).to_csv('./towers_min.csv')
towers.to_csv('bhopal_towers.csv',index=False)