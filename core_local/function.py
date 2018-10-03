import sys, json

def add(num):
    x = num['x']
    y = num['y']
    print(x + y)

def multiply(num):
    x = num['x']
    y = num['y']
    print(x * y)

for line in sys.stdin:
    j = json.loads(line)

fName = j['funcName']
value = j['value']

globals()[fName](value)
