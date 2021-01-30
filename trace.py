#!/usr/bin/env python3
import requests #for ip geodata
import os, sys, platform #for command line interaction and basic functionality
import subprocess
import re

import time as t #for program execution time
start_time = t.time()

#check if tabulate module is installed
from pip._internal.utils.misc import get_installed_distributions
installed_packages = [package.project_name for package in get_installed_distributions()]
if 'tabulate' not in installed_packages:
    print("Please install tabulate with: `pip install tabulate` (24kb)")
    quit()
from tabulate import tabulate

# define platform for cmd line tools
if platform.system() == "Darwin" or platform.system() == "Linux":
    clear=lambda:os.system('clear')
elif platform.system() == "Windows":
    clear=lambda:os.system('cls')

#parse command line arguments
IP = sys.argv[1]
args = sys.argv[2:]
max = "20"
stats = False
for a in range(len(args)):
    b = args[a]
    if b == "-m":
        max = args[a+1]
    if b == "-i":
        stats = True

#start process
proc = subprocess.Popen(["traceroute -m "+max+" -n "+IP], stdout=subprocess.PIPE, shell=True, universal_newlines=True)

clear()
print("Tracing...")

m = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$") #regex for IPv4
totalTime, u, lastip, ipList = 0,0,"0.0.0.0",[]

#main loop
for l in proc.stdout:
    print(l,end="")
    hip = l.split()

    if hip[1] == "*" or hip[1] == "to":
        continue

    hopIP,time = (hip[0],hip[1:]) if m.match(hip[0]) else (hip[1],hip[2:])
    u+=1

    #check if on same network according to IPv4 standard
    ipSplit = [int(a) for a in hopIP.split(".")]
    ipSplitLast = [int(a) for a in lastip.split(".")]
    same = False
    if ipSplit[0] < 128:
        if ipSplit[0] == ipSplitLast[0]:
            same = True
    elif ipSplit[0] < 192:
        if ipSplit[0] == ipSplitLast[0] and ipSplit[1] == ipSplitLast[1]:
            same = True
    elif ipSplit[0] < 224:
        if ipSplit[0] == ipSplitLast[0] and ipSplit[0] == ipSplitLast[0] and ipSplit[0] == ipSplitLast[0]:
            same = True

    #Calc total time
    if "*" in time: time.remove("*")
    totalTime += sum([float(time[a]) for a in range(0,len(time),2)])

    #if not on same network, append
    if same != True:
        ipList.append([hopIP,totalTime])
        totalTime = 0
    lastip = hopIP

#format for prettyprint
i = 0
table = []
for ip in ipList:
    i+=1
    url = "https://geolocation-db.com/json/"+ip[0]
    r = requests.get(url)
    data = r.json()

    country = data["country_name"] if data["country_name"] != None and data["country_name"] != "Not found" else "."
    city = data["city"] if data["city"] != None and data["city"] != "Not found" else "."
    postal = data["postal"] if data["postal"] != None and data["postal"] != "Not found" else "."
    state = data["state"] if data["state"] != None and data["state"] != "Not found" else "."
    table.append([str(i),ip[0],country,state,city,postal,str(round(ip[1],2))+" ms"])
print("")
print(tabulate(table, headers=["Bounce #","IPv4","Country","State","City","Postal code","Time spent"]))

###optional info
if stats == True:
    totalT = round(t.time() - start_time,2)
    bounceT = round(sum([float(a[6].split(" ")[0]) for a in table]),2)
    reqT = round(totalT - bounceT/1000,2)
    bounceT = str(bounceT/1000)+" s" if bounceT > 1000 else str(bounceT)+" ms" #convert to seconds if t > 1s
    info = [[str(round(totalT,2))+" s",bounceT,str(reqT)+" s",str(u)+" IPs"]]
    print("")
    print(tabulate(info, headers=["Exec. time","Total time bouncing","Total time stuck in req.","Unique IPs visited"]))
print("")