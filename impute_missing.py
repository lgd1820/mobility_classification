# 작성일 : 2020-09-10
# 작성자 : 이권동, 맹주형
# 코드 개요 : 버스 궤적 데이터를 불러와 각 위도, 경도의 결측치를 보정하는 코드

import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp
import os
import csv

# main 함수
def impute_main():
    cwd = os.getcwd()
    load_path = cwd + '/data/bus/bus_missing_trajectory/'
    save_path = cwd + '/data/bus/bus_correct_trajectory/'
    version_list = os.listdir(load_path)
    for ver_i in version_list:
        # 143.5 오류나서 파일 확인해야함
        if not "143.5" in ver_i: continue
        version_path = load_path + ver_i
        file_list = os.listdir(version_path) # 지정된 디렉토리의 모든 파일의 경로를 리스트에 저장
        for f in file_list:
            read_path = load_path + ver_i + "/" + f
            write_path = save_path + ver_i + "/"
            if not (os.path.isdir(write_path)): # !!권동이 작성 필요!!
                os.makedirs(os.path.join(write_path))
            c_time, c_lat, c_lng, file_i = convert_data(read_path) # 궤적 데이터의 각 속성을 추출
            e_lat = impute_missing_value(c_lat[:]) # 위도 보정
            e_lat = list(np.array(e_lat))
            e_lng = impute_missing_value(c_lng[:]) # 경도 보정
            e_lng = list(np.array(e_lng))
            with open (write_path + file_i, 'w', newline='') as w_01: # 보정된 데이터를 csv 포멧으로 저장
                w_csv = csv.writer(w_01)
                for i in range(len(c_time)): 
                    w_csv.writerow([c_time[i], e_lat[i], e_lng[i]])

# txt파일에 문자열 데이터 형식으로 저장된 nan 값을 np.nan으로 변경
# 또한 각 속성 별로 각각 다른 리스트에 저장하여 반환
# 매개변수
# load_path : 궤적 파일이 저장된 경로
def convert_data(load_path):
    file_i = load_path.split("/")[-1]
    time_list = []
    lat_list = []
    lng_list = []
    with open(load_path, 'r') as r_01:
        while True :
            line = r_01.readline().replace('\n', '')
            if not line : break
            line_list = line.split(',')
            time = line_list[0]
            lat = line_list[1]
            lng = line_list[2]
            if time == 'np.nan':
                time = np.nan
            else:
                time = float(time)
            if lat == 'np.nan':
                lat = np.nan
            else:
                lat = float(lat)
            if lng == 'np.nan':
                lng = np.nan
            else:
                lng = float(lng)
            time_list.append(time)
            lat_list.append(lat)
            lng_list.append(lng)
    return time_list, lat_list, lng_list, file_i

# tensorflow porbability API를 사용하여, 1차원 벡터 데이터를 보정
# (단, nan값 뿐만 아니라 모든 값들이 보정되므로, nan값의 인덱스를 따로 저장했다가 보정된 nan값과 나머지 원본 데이터를 재취합 시켜줘야함)
# 매개변수
# input_data : 1차원 벡터 데이터 (nan값이 포함된)
def impute_missing_value (input_data):
    time_series_with_nans = input_data
    print('AAA_time_series:', time_series_with_nans)

    observed_time_series = tfp.sts.MaskedTimeSeries(
    time_series=time_series_with_nans,
        is_missing=tf.math.is_nan(time_series_with_nans))
    print('AAA_observerd_time_series:', observed_time_series)

    # Build model using observed time series to set heuristic priors.
    linear_trend_model = tfp.sts.LocalLinearTrend(
        observed_time_series=observed_time_series)
    print('AAA_liner_trend:', linear_trend_model)

    model = tfp.sts.Sum([linear_trend_model],
        observed_time_series=observed_time_series)
    print('AAA_model:', model)

    # Fit model to data
    parameter_samples, _ = tfp.sts.fit_with_hmc(model, observed_time_series)
    print('AAA_parameter:', parameter_samples)

    # Forecast
    forecast_dist = tfp.sts.forecast(model, observed_time_series,
        num_steps_forecast=5, parameter_samples = parameter_samples)
    print('AAA_fore_dist:', forecast_dist)

    # Impute missing values
    observations_dist = tfp.sts.impute_missing_values(
        model, observed_time_series, parameter_samples = parameter_samples)
    print('AAA_observation_dist:', observations_dist)
    print('AAA_time_series:', time_series_with_nans)

    print('imputed means and stddevs: ',
        observations_dist.mean(),
        observations_dist.stddev())
    return observations_dist.mean()

#with tf.device('/device:XLA_CPU:0'):
impute_main()
