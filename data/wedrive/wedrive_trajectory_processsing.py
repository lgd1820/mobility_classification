from haversine import haversine
from datetime import datetime
from math import *
import numpy as np
import json
import xmltodict
import xml.etree.ElementTree as ET
import csv
import os
import codecs

slat = 37.418024
slng = 126.774761
elat = 37.712081
elng = 127.190850

dlat = elat - slat
dlng = elng - slng
cell_lat = dlat/370
cell_lng = dlng/330

def bearing(s_lat, s_lng, e_lat, e_lng):
    lat1 = radians(s_lat)
    lat2 = radians(e_lat)
    diffLong = radians(e_lng - s_lng)

    b_x = sin(diffLong) * cos(lat2)
    b_y = cos(lat1) * sin(lat2) - (sin(lat1) * cos(lat2) * cos(diffLong))
    initial_bearing = atan2(b_x, b_y)
    initial_bearing = degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360 
    return int(compass_bearing)

def wedrive_trajectory_grid(PATH):

    with open(PATH + "wedrive_bus\\trajectory2.txt", 'r') as f:
        npl = []
        count = 0
        print(count)
        while True:
            line = f.readline()
            if not line :
              npl = np.array(npl)
              np.save(PATH + "test_data\\wedrive_grid2.npy", npl)
              break
            s_time = 0
            e_time = 0
            x = 0
            y = 0
            l = [ [(0,0) for _ in range(100)] for _ in range(100)]
            trajectory = json.loads(line.replace("'","\""))
            
            is_in = 0
            is_end = 0
            p_lat = 0
            p_lng = 0
            for t in trajectory:
                grid_x = int((t["lat"]-slat)/cell_lat)
                grid_y = int((t["lng"]-slng)/cell_lng)

                if (grid_x >= 87 and grid_x < 187) and (grid_y >= 112 and grid_y < 212):
                    if x == 0 and y == 0 and s_time == 0 and e_time == 0:
                        if "date" in t.keys():
                            s_time = datetime.strptime(t['date'],"%Y-%m-%d %H:%M:%S")
                        else:
                            s_time = t["time"]
                        x = grid_x
                        y = grid_y
                        p_lat = t["lat"]
                        p_lng = t["lng"]
                        continue

                    if x != grid_x or y != grid_y:
                        if "date" in t.keys():
                            e_time = datetime.strptime(t['date'],"%Y-%m-%d %H:%M:%S")
                            escape_time = (e_time - s_time).seconds
                            s_time = e_time
                        else:
                            escape_time = t["time"] - s_time
                            s_time = t["time"]

                        if l[(x-87)][(y-112)] == (0, 0):
                            l[(x-87)][(y-112)] = (escape_time,bearing(p_lat,p_lng,t["lat"],t["lng"]))
                        else:
                            break
                    is_in = 1
                else:
                    if is_in == 1:
                        is_end = 1
                        break

            if is_in == 1:
                npl.append(l)
                count += 1
                if count % 1000 == 0:
                    print(count)
                with open(PATH + "test_data\\wedrive_grid2.txt", 'a') as g:
                    g.write(str(trajectory[1:]) + "\n")

cwd = os.getcwd()
path = cwd + "\\mode\\data\\"

wedrive_trajectory_grid(path)
