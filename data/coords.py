import pandas as pd
df=pd.read_csv('404.csv')
print(df)
#w 23.288657,77.253617
#e 23.290549,77.567319
# n 23.340995
# s 23.138466
# for i in df:
#     if(i.lat<=23.340995 and i.lat<=23.138466):
#         if(i.lon>=77.253617 and i.lon<=77.567319):
#             print(i)
df2=df[(df["lat"]<=23.340995) & (df["lat"]>=23.138466) & (df["lon"]<=77.567319) & (df["lon"]>=77.253617)]
print(df2)
df2.to_csv('bhopal_towers.csv',index=False)