import numpy as np
import os
import time
from datetime import datetime, timedelta
from haversine import haversine

def processing_main():
    interval_distance = 100
    cwd = os.getcwd()
    load_path = cwd + '/data/wedrive_bus/bus_trajectory/'
    save_path = cwd + '/data/bus_missing_trajectory/'
    #remove_list = os.listdir(save_path)
    #for remove_file in remove_list:
    #    os.remove(save_path + remove_file)
    processing_data(interval_distance, load_path, save_path)

def write_file(time, lat, lng, save_path, file_i):
    with open (save_path + file_i, 'a') as add_01:
        add_01.write(str(time) + ',' + lat + ',' + lng + '\n')

def convert_to_stamp(time):
    time = datetime.strptime(time,'%Y%m%d%H%M%S')
    time_stamp = time.timestamp()
    return time_stamp

def calculate_time(past_time, time):
    time_01 = datetime.strptime(past_time,'%Y%m%d%H%M%S')
    time_02 = datetime.strptime(time,'%Y%m%d%H%M%S')
    return (time_02 - time_01).seconds

def calculate_distance(p_lat, p_lng, lat, lng):
    point = (float(lat), float(lng))
    p_point = (float(p_lat), float(p_lng))
    dis_meter = (haversine(p_point, point))*1000
    return dis_meter
    

def processing_data(interval_distance, load_path, save_path):
    version_list = os.listdir(load_path)
     
    missing_value = 'np.nan,np.nan'
    for ver_i in version_list:
        open_path = load_path + ver_i
        file_list = os.listdir(open_path)
        #print(file_list)
        for file_i in file_list:
            if not (os.path.isdir(save_path + ver_i)):
                os.makedirs(os.path.join(save_path + ver_i))
            X_list = []
            Y_list = []
            with open(open_path + "/" + file_i, 'r') as r_01:
                line = r_01.readline().replace('\n', '')
                line_list = line.split(',')
                time = line_list[0]
                lat = line_list[1]
                lng = line_list[2]
                past_time = time
                p_lat = lat
                p_lng = lng
                time = convert_to_stamp(time)
                line = str(time) + ',' + lat + ',' + lng
                write_file(time, lat, lng, save_path + ver_i + "/", file_i)
                while True :
                    line = r_01.readline().replace('\n', '')
                    if not line : break
                    line_list = line.split(',')
                    time = line_list[0]
                    lat = line_list[1]
                    lng = line_list[2]
                    time_dist = float(calculate_time(past_time, time))
                    distance = calculate_distance(p_lat, p_lng, lat, lng)
                    num_missing = int(float(distance)/interval_distance)-1

                    if num_missing > 0:
                        plus_time = int(float(time_dist)/(num_missing+1))
                    time_stamp = int(convert_to_stamp(time))
                    line = lat + ',' + lng
                    for i in range (num_missing):
                        time_nan = int(convert_to_stamp(past_time)) + plus_time*(i+1)
                        write_file(time_nan, 'np.nan', 'np.nan', save_path + ver_i + "/", file_i)
                    write_file(time_stamp, lat, lng, save_path + ver_i + "/", file_i)

                    past_time = time
                    p_lat = lat
                    p_lng = lng
processing_main()
