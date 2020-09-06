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

# MySQL 에서 가져온 위드라이브 궤적 데이터를 그리드로 변환하여 함수npz 형태와 궤적을 같이 저장하는 함수
# 오류 수정 20-03-15
# PATH : 위드라이브 궤적 데이터의 경로(string)
def wedrive_trajectory_grid(PATH):
    with open(PATH, 'r') as f:
        npl = []
        while True:
            line = f.readline()
            if not line :
              npa = np.array(npl)
              np.savez("wedrive_grid2.npz", X_data = npa)
              break
            s_time = 0
            e_time = 0
            x = 0
            y = 0
            l = [ [(0,0) for _ in range(100)] for _ in range(100)]
            trajectory = json.loads(line.replace("'","\""))
            is_in = 0
            for t in trajectory[1:]:
                grid_x = int((t['lat'] - slat)/cell_lat)
                grid_y = int((t['lng'] - slng)/cell_lng)
                lat = t['lat']
                lng = t['lng']
                p_lat = 0
                p_lng = 0
                if (x == 0 or y == 0):
                    x = grid_x
                    y = grid_y
                    p_lat = lat
                    p_lng = lng
                    s_time = datetime.strptime(t['time'],"%H:%M:%S")
                else:
                    if x != grid_x or y != grid_y:
                        e_time = datetime.strptime(t['time'],"%H:%M:%S")
                        escape_time = e_time - s_time
                        s_time = e_time
                        try:
                            if (x >= 87 and x < 187) and (y >= 112 and y < 212):
                                if l[(x-87)][(y-112)] == (0,0):
                                    l[(x-87)][(y-112)] = (escape_time.seconds//60,bearing(p_lat,p_lng,lat,lng))
                                    is_in = 1
                                else:
                                    continue
                            else:
                                continue
                        except Exception as e:
                            print(e)
                            continue
            if is_in == 1:
                npl.append(l)
                # 실제로 분류된 데이터를 확인하기 위한 파일
                with open('wedrive_grid2.txt', 'a') as g:
                    g.write(str(trajectory[:1]) + "\n")

# 공공 데이터에서 받아온 로우 데이터를 버스 별로 궤적을 추출하는 함수
# 오류 수정 3-15
# VERSION : string 또는 int 의 숫자 raw 데이터의 .n 형태의 번호
# 추후 리스트로 변경해서 여러 버전을 한번에 하도록 수정할 예정
def bus_trajectory(VERSION):
    ver = "." + str(VERSION)
    files = os.listdir('./bus_raw/')
    print(files, ver)
    for filename in files:
        bus_gps_list = {}
        if ver not in filename: continue
        with codecs.open("./bus_raw/" + filename, 'r', encoding='utf-8') as f:
            while True:
                try:
                    line = f.readline()
                except: break
                if not line: break
                x = json.dumps(xmltodict.parse(line))
                j = json.loads(x)
                try: itemList = j['ServiceResult']['msgBody']['itemList']
                except Exception: break
                if type(itemList) is dict: itemList = [itemList]
                for item in itemList:
                    if type(item) is dict:
                        if item['vehId'] in bus_gps_list:
                            gps_list = bus_gps_list[item['vehId']]
                            gps_list.append([item['dataTm'], item['tmY'],item['tmX'],])
                        else:
                            gps_list = [item['dataTm'], item['tmY'],item['tmX']]
                            bus_gps_list[item['vehId']] = [gps_list]
            f.close()
        for key in bus_gps_list.keys():
            if not (os.path.isdir('./bus_trajectory/' + filename)):
                os.makedirs(os.path.join('./bus_trajectory/' + filename))
            with open('./bus_trajectory/' + filename + '/'  + key + ".csv", 'w') as c:
                wr = csv.writer(c)
                for l in bus_gps_list[key]:
                    wr.writerow([l[0],l[1],l[2]])
            c.close()

# 버스 정거장의 위치 그리드를 알기위한 함수
def get_bus_grid():
    bus_station_grid = []
    cwd = os.getcwd() + "\\mode\\data\\wedrive_bus"
    files = os.listdir(cwd + "\\bus_station\\")
    for filename in files:
        # csv 파일은 정제한 데이터
        if ".csv" not in filename:
            continue
        with open(cwd + "\\bus_station\\" + filename, "r") as f:
            while True:
                line = f.readline()
                if not line: break
                l = line.replace("\n","").replace("\r","").split(",") 
                grid_lat = int((float(l[1]) - slat)//cell_lat)
                grid_lng = int((float(l[2]) - slng)//cell_lng)
                bus_station_grid.append((grid_lat, grid_lng))
    
    return bus_station_grid

# 학습 데이터를 만들기 위해 슬라이스가 포함된 그리드 변환 함수
# 오류 수정 04-25
def bus_trajectory_grid():
    cut_size = 5
    stride_size = 1
    cwd = os.getcwd() + "\\mode\\data\\wedrive_bus"

    directorys = os.listdir(cwd + "\\bus_trajectory")
    for dname in directorys:
        files = os.listdir(cwd + "\\bus_trajectory\\" + dname)
        for filename in files:
            with open(cwd + "\\bus_trajectory\\" + dname + "\\" + filename) as f:
                lines = csv.reader(f,delimiter = ",")
                s_time = 0
                e_time = 0
                x = 0
                y = 0
                cut_list = []
                bus_station = get_bus_grid()
                bus_station_num = 0
                l = [ [(0,0) for _ in range(100)] for _ in range(100)]
                for line in lines:
                    grid_x = int((float(line[1])-slat)/cell_lat)
                    grid_y = int((float(line[2])-slng)/cell_lng)
                    lat = float(line[1])
                    lng = float(line[2])
                    p_lat = 0 
                    p_lng = 0 
                    #print(grid_x, grid_y)
                    if (x == 0 or y == 0): 
                        x = grid_x
                        y = grid_y
                        p_lat = lat 
                        p_lng = lng
                        s_time = datetime.strptime(line[0],"%Y%m%d%H%M%S")
                    else:
                        if x != grid_x or y != grid_y:
                            e_time = datetime.strptime(line[0],"%Y%m%d%H%M%S")
                            escape_time = e_time - s_time
                            try:
                                if (x >= 87 and x < 187) and (y >= 112 and y < 212):
                                    if l[(x-87)][(y-112)] == (0,0):
                                        l[(x-87)][(y-112)] = (escape_time.seconds//60,bearing(p_lat,p_lng,lat,lng))
                                        is_in = 1
                                    else:
                                        continue
                                else:
                                    continue
                            except Exception as e:
                                print(e)
                                continue

                            if (x,y) in bus_station:
                                cut_list.append((x,y,escape_time.seconds//60,bearing(p_lat,p_lng,lat,lng),1))
                            else:
                                cut_list.append((x,y,escape_time.seconds//60,bearing(p_lat,p_lng,lat,lng),0))
                            x = grid_x
                            y = grid_y
                            p_lat = lat
                            p_lng = lng
                            s_time = e_time

                list_len = len(cut_list)
                list_by_station = []
                l = []
                for i in range(0, list_len):
                    if cut_list[i][4] == 1:
                        l.append(cut_list[i])
                        list_by_station.append(l)
                        l = []
                    elif cut_list[i][4] == 0:
                        l.append(cut_list[i])
                list_len = len(list_by_station)
                if not (os.path.isdir(cwd + "\\bus_study")):
                    os.makedirs(os.path.join(cwd + "\\bus_study"))
                cut_file = open(cwd + "\\bus_study\\" + filename, "w")
                for i in range(0, (list_len - cut_size), stride_size):
                    cl = []
                    if (i + cut_size) >= list_len:
                        break
                    cut_shape = [ [(0,0) for _ in range(100)] for _ in range(100)]
                    for s in list_by_station[i]:
                        print(s, s[0])
                        cut_shape[s[0]-87][s[1]-112] = (s[2],s[3])
                    if not(os.path.isdir(cwd + "\\bus_study")):
                        os.makedirs(os.path.join(cwd + "\\bus_study"))                
                    cut_file.write(str(cut_shape)+"\n")
