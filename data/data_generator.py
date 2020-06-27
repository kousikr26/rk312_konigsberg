import random
import os
import csv
import time

n=1000 #records
start_date="1-6-2020"
start_time="1:30:45"
end_date="20-6-2020"
end_time="21:30:55"
towerIDS=list(range(100,999))





start=start_date+" "+start_time
end=end_date+" "+end_time
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

fields=["Caller","Receiver","Date","Time","Duration","TowerID","IMEI"]
def phoneNumber():
    return random.randint(7000000000,9999999999)
def imei():
    tmp=""
    for i in range(15):
        x=random.randint(0,9)
        tmp+=str(x)
    return tmp

nums=[]
calls=[]
for i in range(int(n/5)):
    nums.append(phoneNumber())
for x in nums:
    num_calls=random.randint(0,10)
    while(num_calls):
        y=random.choice(nums)
        if(y!=x):
            num_calls-=1
            calls.append([x,y])

for i in range(len(calls)):
    t=random_date(start,end,random.random())
    calls[i].append(getDate(t))
    calls[i].append(getTime(t))
    calls[i].append(random.randint(1,100))
    calls[i].append(random.choice(towerIDS))
    calls[i].append(imei())
print(calls)
print(len(calls))

with open('data.csv','w',newline='') as file:
    writer=csv.DictWriter(file,fieldnames=fields)
    writer.writeheader()
    for i in range(len(calls)):
        tmp={}
        for j in range(len(fields)):
            tmp[fields[j]]=calls[i][j]
        writer.writerow(tmp)
