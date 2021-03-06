import random
import os
import csv
import time
import decimal
from datetime import datetime
import pandas as pd
import numpy as np

n = 1000  # records
start_date = "1-6-2020"
start_time = "1:30:45"
end_date = "20-6-2020"
end_time = "21:30:55"
end_date2 = "1-6-2020"
end_time2 = "13:30:55"

towerIDS = pd.read_csv('data/data.csv')['TowerID'].unique()




start = start_date+" "+start_time
end = end_date+" "+end_time

end2 = end_date2+" "+end_time2

def private_ip():
    x1 = random.choice([172, 192, 10])
    if int(x1) == 172:
        x2 = random.randint(16, 31)
        x3 = random.randint(0, 255)
        x4 = random.randint(0, 255)
        return ".".join(map(str, ([x1, x2, x3, x4])))
    else:
        x2 = random.randint(0, 255)
        x3 = random.randint(0, 255)
        x4 = random.randint(0, 255)
        return ".".join(map(str, ([x1, x2, x3, x4])))


def public_ip():
    allowed_values = list(range(0, 256))
    allowed_values.remove(10)
    allowed_values.remove(192)
    allowed_values.remove(172)
    ip=".".join(map(str, (random.choice(allowed_values) for _ in range(4))))
    return ip
def port():
	return random.randint(0000,9999)

def dest_port():
    allowed_values = ['5223','5228', '4244', '5222', '5242', '443_','443', '3478-3481', '49152-65535', '80', '8080', \
        '443', '8081', '993', '143', '8024', '8027', '8013', '8017', '8003', '7275', '8025', '8009', '58128',\
             '51637', '61076', '40020', '40017', '40023', '40019', '40001', '40004', '40034', '40031', '40029', '40005',\
                  '40026', '40008', '40032']
    return random.choice(allowed_values)

def get_msisdn():
	return random.randint(100000000000,999999999999)   #12-digit for now

def str_time_prop(start, end, format, prop):
    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))
    ptime = stime + prop * (etime - stime)
    return time.localtime(ptime)


def random_date(start, end, prop):
    return str_time_prop(start, end, '%d-%m-%Y %H:%M:%S', prop)

def getDate(t):
    return time.strftime("%d-%m-%Y",t)
def getTime(t):
    return time.strftime("%H:%M:%S",t)    

def volume():
    return float(decimal.Decimal(random.randrange(0, 10))/100)

def rat_type():
    allowed_values = ['2G','3G']
    return random.choice(allowed_values)

fields=["IMEI","Private IP","Private Port", "Public IP", "Public Port", "Dest IP","DEST PORT", "MSISDN", "IMSI", "Start Date","Start Time","Duration", "CELL_ID", "Uplink Volume","Downlink Volume","Total Volume","I_RATTYPE"]

ph_numbers = np.union1d(pd.read_csv('data/data.csv')['Caller'].unique(),pd.read_csv('data/data.csv')['Receiver'].unique())


def imei():
    return random.randint(7000000000,9999999999)

nums=[] #ip_addresses
calls=[] # records
print(ph_numbers)
for x in ph_numbers:
    nums.append(x)
for x in nums:
    num_calls= 50 #random.randint(50,100)
    #while num_calls :
    #    num_calls-=1
    for _ in range(num_calls):
        w =[private_ip(),port(),public_ip(),port()]
        y,z= public_ip(), dest_port()
        calls.append([x]+w+[y,z])
#print(nums)    
print(len(nums))
print(len(calls))
for i in range(len(calls)):
    t1=random_date(start,end,random.random())
    #print(time.strftime('%Y-%m-%dT%H:%M:%SZ', t1))
    #t2=random_date(start,end2,random.random())
    calls[i].append(get_msisdn())
    calls[i].append(imei())
    calls[i].append(getDate(t1)) # start date
    calls[i].append(getTime(t1)) # start time
    calls[i].append(random.randint(1,70))  # Duration
    calls[i].append(random.choice(towerIDS))

    v1 = volume()
    v2=volume()
    calls[i].append(v1)
    calls[i].append(v2)
    calls[i].append(v1+v2)
    calls[i].append(rat_type())
    
    
    
    

#print(calls)

#print(public_ip())

with open('data/ipdr_data.csv','w',newline='') as file:
    writer=csv.DictWriter(file,fieldnames=fields)
    writer.writeheader()
    for i in range(len(calls)):
        tmp={}
        for j in range(len(fields)):
            tmp[fields[j]]=calls[i][j]
        writer.writerow(tmp)
