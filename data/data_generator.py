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
towerIDS=['40478-25121-16152','404-732721-29792','404-7825121-16152','404-732721-29792','404-102005-2364641','404-102005-233197825','404-733102-21102887','404-3811016-72558384','404-4534204-27529358','404-3810-12032','404-40501-24401','404-458211-21193','404-458211-14224','404-45541-40181','404-458211-14222','404-4523361-45973','404-4523361-49511','404-4523361-5062','404-4523361-14843','404-4523361-18202','404-4523361-49513','404-4523361-14842','404-4523361-10732','404-4523361-50883','404-4521792-14032','404-4521792-273']




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
