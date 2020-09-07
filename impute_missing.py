import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp
import os
import csv

def impute_main():
    cwd = os.getcwd()
    load_path = cwd + '/data/bus_missing_trajectory/'
    save_path = cwd + '/data/bus_correct_trajectory/'
    version_list = os.listdir(load_path)
    for ver_i in version_list:
        if not "143.5" in ver_i: continue
        version_path = load_path + ver_i
        file_list = os.listdir(version_path)
        for f in file_list:
            read_path = load_path + ver_i + "/" + f
            write_path = save_path + ver_i + "/"
            if not (os.path.isdir(write_path)):
                os.makedirs(os.path.join(write_path))
            c_time, c_lat, c_lng, file_i = convert_data(read_path)
            e_lat = impute_missing_value(c_lat[:])
            e_lat = list(np.array(e_lat))
            e_lng = impute_missing_value(c_lng[:])
            e_lng = list(np.array(e_lng))
            with open (write_path + file_i, 'w', newline='') as w_01:
                w_csv = csv.writer(w_01)
                for i in range(len(c_time)): 
                    w_csv.writerow([c_time[i], e_lat[i], e_lng[i]])

def convert_data(load_path):
    file_i = load_path.split("/")[-1]
    time_list = []
    lat_list = []
    lng_list = []
    with open(load_path, 'r') as r_01:
        while True :
#           for i in range (30) :
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
