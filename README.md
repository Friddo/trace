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

Program will return error, if the tabulate package is missing:
```
$ python3 trace.py github.com
Please install tabulate with: `pip install tabulate` (24kb)
```
