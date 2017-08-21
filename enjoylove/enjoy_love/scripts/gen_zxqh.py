#coding:utf-8
import csv
import json

__author__ = 'yuwhuawang'
__created__ = '2017/08/20 14:50'


def load():
    with open('xzqh.json') as json_file:
        data = json.load(json_file)
        return data


s = load()
xzqh_new = {"provinces":{}}
for city in s:
    if city['bm'][2:6] == "0000":
        #print city['bm']
        #print city['mc']
        xzqh_new['provinces'][city['bm']] = ({"name":  city['mc'], "id":city['bm'], "cites":{}})

    elif city['bm'][4:6] == "00":
        #print city['bm']
        #print city['mc']
        xzqh_new['provinces'][city['bm'][0:2]+"0000"]["cites"][city['bm']] = ({"name":  city['mc'], "id":city['bm'], "counties":{}})

    else:

        #print city['bm']
        #print city['mc']
        xzqh_new['provinces'][city['bm'][0:2]+"0000"]["cites"][city['bm'][0:4]+"00"]['counties'][city['bm']] = ({"name":  city['mc'], "id": city['bm']})

#print xzqh_new
result = []


for k, x in xzqh_new.items():
    #print k,x

    for y in x.values():
        next_2 = []
        for z in y['cites'].values():
            next_3 = []
            for t in z['counties'].values():
                next_3.append({
                    "name":t['name'],
                    "code":t['id'],
                    "next":[]
                })
            next_2.append({
                    "name":z['name'],
                    "code":z['id'],
                    "next":next_3
            })

        result.append({
            "name":y['name'],
            "code":y['id'],
            "next":next_2
        })

def store(data):
    with open('data.json', 'w') as json_file:
        json_file.write(json.dumps(data))

print result

store(result)
