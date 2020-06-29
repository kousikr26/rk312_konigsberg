from django.shortcuts import render
import pandas as pd
# Create your views here.
def csv_to_json():
    df=pd.read_csv('data.csv')
    
