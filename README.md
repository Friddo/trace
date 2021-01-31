# trace
Simple python script for a more descriptive traceroute command

# Guide

```
python3 trace.py [-m] [-i] IP
```
where:  
`-m`: max network bounces, default = 20  
`-i`: show additional info  
**IP can be either web address or in the IPv4 standard**

# Dependencies

* tabulate
* requests


Program will return error, if the tabulate or requests package is missing:
```
$ python3 trace.py github.com
Please install tabulate with: `pip install tabulate` (24kb)
Please install requests with: `pip install requests` (61kb)
```
