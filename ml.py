import pandas as pd
from datetime import datetime

import numpy as np 
from scipy import stats 
import matplotlib.pyplot as plt 
import matplotlib.font_manager 
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

df = pd.read_csv('./data/final_data.csv')
towers=pd.read_csv('./data/towers_min.csv')
def anomalies(df,algo="IsolationForest",contamination=0.001):
    cdr_df=pd.merge(df,towers[['lat','lon','TowerID']],on='TowerID')
    cdr_df=cdr_df[["Caller","Receiver","Time","Duration","lat","lon"]]
    # cdr_df['Date']=pd.to_datetime(cdr_df['Date'],format='%d-%m-%Y')
    cdr_df['Time']=pd.to_datetime(cdr_df['Time'],format='%H:%M:%S')
    cdr_df["Time"]=cdr_df["Time"].apply(lambda x: (x - x.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
    if (algo=="IsolationForest"):
        iso=IsolationForest(contamination=contamination)
    elif(algo=="EllipticEnvelope"):
        iso=EllipticEnvelope(contamination=contamination)
    elif(algo=="LocalOutlierFactor"):
        iso=LocalOutlierFactor(contamination=contamination)
    mask=iso.fit_predict(cdr_df[["Time","Duration","lat","lon"]])==-1
    cdr_df=cdr_df[mask]
    # print(cdr_df)


anomalies(df)