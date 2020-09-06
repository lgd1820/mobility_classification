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

def get_bus_grid():
    bus_station_grid = []
    cwd = os.getcwd() + "\\mode\\data\\wedrive_bus"
    files = os.listdir(cwd + "\\bus_station\\")
    for filename in files:
        # csv 파일은 정제한 데이터
        if ".csv" not in filename:
            continue
        with open(cwd + "\\bus_station\\" + filename, "r", encoding='UTF-8') as f:
            while True:
                line = f.readline()
                if not line: break
                l = line.replace("\n","").replace("\r","").split(",") 
                grid_lat = int((float(l[1]) - slat)//cell_lat) - 87
                grid_lng = int((float(l[2]) - slng)//cell_lng) - 112
                if ((grid_lat > 99 or grid_lat <= -1) or (grid_lng >= 101 or grid_lng <= -1)):
                    continue
                bus_station_grid.append((grid_lat, grid_lng))
    
    return bus_station_grid

def bus_trajectory():
    cwd = os.getcwd() + "\\mode\\data"
    directorys = os.listdir(cwd + "\\bus_correct_trajectory") 
    trajectory = []
    for dname in directorys:
        if not "143" in dname: continue
        files = os.listdir(cwd + "\\bus_correct_trajectory\\" + dname)
        for filename in files:
            with open(cwd + "\\bus_correct_trajectory\\" + dname + "\\" + filename) as f:
                lines = csv.reader(f,delimiter = ",")
                p_time = 0
                x = 0
                y = 0
                cut_list = []
                p_lat = 0
                p_lng = 0
                is_in = 0
                is_end = 0
                for line in lines:
                    grid_x = int((float(line[1])-slat)/cell_lat)
                    grid_y = int((float(line[2])-slng)/cell_lng)
                    if (grid_x >= 87 and grid_x < 187) and (grid_y >= 112 and grid_y < 212):
                        if len(cut_list) == 0:
                            p_time = int(float(line[0]))
                        else:
                            if (int(float(line[0])) - p_time) == 0:
                                continue
                        lat = float(line[1])
                        lng = float(line[2])
                        time = int(float(line[0]))
                        cut_list.append([grid_x - 87, grid_y - 112, lat, lng, time])
                        p_time = time
                        is_in = 1
                        x = grid_x
                        y = grid_y
                    else:
                        if is_in == 1:
                            trajectory.append(cut_list)
                            is_end = 1
                            break
                if is_in == 1 and is_end == 0:
                    trajectory.append(cut_list)
    return trajectory

def make_slice(cut_size_list=None, stride_size_list=None):
    trajectory_list = bus_trajectory()
    bus_station_list = get_bus_grid()
    slice_trajectory = []
    for trajectory in trajectory_list:
        trajectory_in_bustation = []
        count = 0
        for gps in trajectory:
            if (gps[0], gps[1]) in bus_station_list:
                trajectory_in_bustation.append(count)
                count += 1
                
        for cut_size in cut_size_list:
            for stride_size in stride_size_list:
                from_n = 0
                to_n = cut_size - 1
                while(True):
                    if to_n >= len(trajectory_in_bustation) - 1:
                        if len(trajectory_in_bustation) == 0:
                            slice_trajectory.append(trajectory)
                            break
                        slice_trajectory.append(trajectory[trajectory_in_bustation[from_n]:])                  
                        break
                    slice_trajectory.append(trajectory[trajectory_in_bustation[from_n]:trajectory_in_bustation[to_n]])
                    from_n += stride_size
                    to_n += stride_size
        slice_trajectory.append(trajectory)
        #print(len(trajectory_in_bustation))
    return slice_trajectory
    
def save_grid():
    slice_trajectory = make_slice(cut_size_list=[i for i in range(4, 32, 2)], stride_size_list=[1])
    dataset = []
    for sc in slice_trajectory:
        cell = [[(0,0) for _ in range(100)] for _ in range(100)]
        p_time = 0
        for i in range(len(sc)):
            time = 0
            if i == 0:
                time = 0
                heading = bearing(sc[i][2], sc[i][3], sc[i+1][2], sc[i+1][3])
            elif i == len(sc) -1:
                time = (sc[i][4] - p_time)
                heading = 0
            else:
                time = (sc[i][4] - p_time)
                heading = bearing(sc[i][2], sc[i][3], sc[i+1][2], sc[i+1][3])
            p_time = sc[i][4]
            cell[sc[i][0]][sc[i][1]] = (time, heading)    
        dataset.append(cell)
    dataset = np.array(dataset)
    print(dataset.shape)
    cwd = os.getcwd() + "\\mode\\data\\study_data\\"
    np.save( cwd + "study_data_missing_even.npy", dataset)

save_grid()
