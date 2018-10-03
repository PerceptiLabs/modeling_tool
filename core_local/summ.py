import sys, json

# simple JSON echo script
for line in sys.stdin:
#    j = json.dumps(json.loads(line))
    j = json.loads(line)

x = j['x']
y = j['y']

#print(x)
#print(y)
print(x+y)
