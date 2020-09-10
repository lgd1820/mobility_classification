'''
작성일 : 2020-09-10
작성자 : 이권동
코드 개요 : 위드라이브 궤적을 불러와 특정 위도, 경도 안에있는 궤적을 2차원 데이터로 전처리하는 코드
'''
from haversine import haversine
from datetime import datetime
from math import *
import numpy as np
import json
import os


#특정 구역 설정
slat = 37.418024
slng = 126.774761
elat = 37.712081
elng = 127.190850

# cell이 가지는 구역 계산
dlat = elat - slat
dlng = elng - slng
cell_lat = dlat/370
cell_lng = dlng/330

'''
    함수 개요 :
        시작 GPS 와 끝 GPS를 이용해 0 ~ 360의 헤딩을 구하는 함수
    매개변수 :
        s_lat, s_lng = 시작 latitude, longitude
        e_lat, e_lng = 끝 latitude, longitude
'''
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

'''
    함수 개요 :
        raw_trajectory에 있는 궤적 파일에서 정해진 구역에 있는 궤적을
        100 x 100 형태의 npy로 저장하는 함수
        더불어 npy의 순서와 똫같이 궤적을 따로 text로 저장함(분류 후 궤적을 플로팅 하기 위한 용도)
'''
def wedrive_trajectory_grid():
    with open("./raw_trajectory/trajectory.txt", 'r') as f:
        npl = []
        count = 0
        print(count)
        while True:
            line = f.readline()

            # 라인이 끝나는 npy 저장
            if not line :
              npl = np.array(npl)
              np.save("./npy/wedrive_grid.npy", npl)
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

                # 현재 GPS 가 구역안에 있는 지 확인
                if (grid_x >= 87 and grid_x < 187) and (grid_y >= 112 and grid_y < 212):
                    
                    # 구역안에 있는 궤적의 첫 시작일 경우
                    if x == 0 and y == 0 and s_time == 0 and e_time == 0:
                        
                        # json 데이터가 datetime과 timestamp로 저장되어있는게 섞여있음
                        # 최신 데이터는 timestamp
                        if "date" in t.keys():
                            s_time = datetime.strptime(t['date'],"%Y-%m-%d %H:%M:%S")
                        else:
                            s_time = t["time"]
                        x = grid_x
                        y = grid_y
                        p_lat = t["lat"]
                        p_lng = t["lng"]
                        continue

                    # CELL 이 이동됐을 경우
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
                with open("./npy/wedrive_grid.txt", 'a') as g:
                    g.write(str(trajectory[1:]) + "\n")

wedrive_trajectory_grid()
