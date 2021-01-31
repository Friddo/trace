#!/usr/bin/env python3
import os, sys, platform, getopt #for command line interaction and basic functionality
import subprocess
import re

import time as t #for program execution time
start_time = t.time()

#check if tabulate module is installed
from pip._internal.utils.misc import get_installed_distributions
installed_packages = [package.project_name for package in get_installed_distributions()]
c = 0
if 'tabulate' not in installed_packages:
    print("Please install tabulate with: `pip install tabulate` (24kb)")
    c = 1
if 'requests' not in installed_packages:
    print("Please install requests with: `pip install requests` (61kb)")
    c = 1
if c: quit()
import requests
from tabulate import tabulate

# define platform for cmd line tools
if platform.system() == "Windows":
    clear=lambda:os.system('cls')
    s = 1
else: #for macOS and linux
    s = 0
    clear=lambda:os.system('clear')

#parse command line arguments
opt, args = getopt.getopt(sys.argv[1:], 'm:i')
max = "20"
stats = False
for a,b in opt:
    if a == "-m":
        max = b
    if a == "-i":
        stats = True
IP = args[0]

#start process
cmd = "C:\\Windows\\System32\\TRACERT.exe -d -4 -h "+max+" "+IP if s else ["traceroute -m "+max+" -n "+IP]
print(cmd)
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, universal_newlines=True)

clear()
print("Tracing...")

m = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$") #regex for IPv4
totalTime, u, lastip, ipList = 0,0,"0.0.0.0",[]

#main loop
for l in proc.stdout:
    print(l,end="")
    if s: #convert to same format as macOS/linux
        if len(l.split()) != 8:
            continue
        tmp = l.split()[:7]
        tmp.insert(1,l.split()[7:][0])
        l = " ".join(tmp)
    hip = l.split()

    if hip[1] == "*" or hip[1] == "to": #for macOS/linux
        continue

    #Extract data
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
        if ipSplit[0] == ipSplitLast[0] and ipSplit[1] == ipSplitLast[1] and ipSplit[2] == ipSplitLast[2]:
            same = True

    #Calc total time
    while "*" in time: time.remove("*")
    while "!Z" in time: time.remove("!Z") #private port
    while "!X" in time: time.remove("!X") #private port

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
print(tabulate(table, headers=["#","IPv4","Country","State","City","Postal code","Time spent"]))

###optional info
if stats == True:
    totalT = round(t.time() - start_time,2)
    bounceT = round(sum([float(a[6].split(" ")[0]) for a in table]),2)
    reqT = round(totalT - bounceT/1000,2)
    bounceT = str(round(bounceT/1000,2))+" s" if bounceT > 1000 else str(bounceT)+" ms" #convert to seconds if t > 1s
    info = [[str(totalT)+" s",bounceT,str(reqT)+" s",str(u)+" IPs"]]
    print("")
    print(tabulate(info, headers=["Exec. time","Total time bouncing","Total time stuck in req.","Unique IPs visited"]))
print("")
