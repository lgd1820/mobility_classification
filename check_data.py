import numpy as np
import csv
import os

slat = 37.418024
slng = 126.774761
elat = 37.712081
elng = 127.190850

dlat = elat - slat
dlng = elng - slng
cell_lat = dlat/370
cell_lng = dlng/330

cwd = os.getcwd()
path = cwd + "\\mode\\data\\test_data\\wedrive_grid2.npy"
#path = cwd + "\\mode\\data\\study_data\\study_data_missing_1.npy"
data = np.load(path)

num = 0
list_num = [1683, 22030]
for d in data:
    num += 1
    if num in list_num:
        
        for i in range(100):
            for j in range(100):
                if d[i][j][0] != 0 or d[i][j][1] != 0:
                    print(d[i][j])
        print("-------")