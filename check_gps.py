# 권동 2020-09-08 18:11 주석 추가
import pandas as pd
import os
import numpy as np
import tensorflow as tf
import csv
import json

def normalize(data):
    data = data.astype(np.float32)
    mean = np.mean(data)
    data -= mean
    std = np.std(data)
    data /= std
    return data

# 위드라이브 궤적 및 모델 파일 read를 위한 path 
cwd = os.getcwd()
test_data_path = cwd + "/mode/data/bus/npy_data/wedrive_grid.npy"
model_name = "asd" # 테스트 할때 입력
model_path = cwd + "/model/" + model_name

test_data = np.load(test_data_path)
test_data = normalize(test_data)
test_data = test_data.reshape(-1, 100, 100, 2).astype('float32')
test_data_label = np.array([1 for _ in range(len(test_data))])
test_data_label = tf.keras.utils.to_categorical(test_data_label, 2)

model = tf.keras.models.load_model(model_path)

predict_y = model.predict(test_data)

# wedrive_grid.txt 파일은 1줄에 궤적 데이터 하나가 저장(JSON)
# npy 파일과 txt 파일의 저장 순서가 같기 때문에 아래 코드로 chekc_gps 폴더 안에 궤적을 CSV 로 저장

l = []
count = 1
for p in predict_y:
    if p[0] > p[1]:
        l.append(count)
    count += 1

print(l)

with open(cwd + "/mode/data//bus/npy_data/wedrive_grid.txt", "r") as f:
    line_count = 0
    while(True):
        line_count += 1
        line = f.readline()
        if line_count in l:
            csv_f = open(cwd + "/mode/check_gps/" + str(line_count) + ".csv", "w", newline="")
            wr = csv.writer(csv_f)
            trajectory = json.loads(line.replace("\'", "\""))
            wr.writerow(["lat", "lng"])
            #print(trajectory)
            for gps in trajectory:
                wr.writerow([gps["lat"], gps["lng"]])
            csv_f.close()
        if not line: break