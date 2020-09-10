# LGD 2020-09-10 18:57 
import pandas as pd
import os
import numpy as np
import tensorflow as tf

# LGD 2020-09-10 18:57
# train 데이터와 test 데이터를 test_size 비율에 따른 split default 값은 8:2
# random_state : 랜덤 시드라서 그대로 두면 됨
# x : data, y: label 
def train_test_split(x, y, test_size=0.2, random_state=1004):
    test_num = int(x.shape[0] * test_size)
    train_num = x.shape[0] - test_num

    if shuffle:
        np.random.seed(random_state)
        shuffled = np.random.permutation(x.shape[0])
        x = x[shuffled,:]
        y = y[shuffled]
        x_train = x[:train_num]
        x_test = x[train_num:]
        y_train = y[:train_num]
        y_test = y[train_num:]
    else:
        x_train = x[:train_num]
        x_test = x[train_num:]
        y_train = y[:train_num]
        y_test = y[train_num:]
    return x_train, x_test, y_train, y_test

# LGD 2020-09-10 18:57
# npy 데이터 정규화
# data : x
def normalize(data):
    data = data.astype(np.float32)
    mean = np.mean(data)
    data -= mean
    std = np.std(data)
    data /= std
    return data

# LGD 2020-09-10 18:57
# 학습데이터와 테스트 데이터를 전처리하는 함수
# 현재 bus data 보다 wedrive data 가 압도적으로 많기 때문에
# 셔플한 wedrive data에서 bus data 의 크기만큼 잘라서 train data로 전처리
# bus data도 20% 만큼 test data에 들어감
# train data에 들어간 wedrive data를 제외하고 wedrive data는 전부 test data로 들어감
def data_processing(bus_data, wedrive_data):
    print('bus_data', bus_data.shape, 'wedrive_data shape:', wedrive_data.shape)

    bus_data = normalize(study_data)
    wedrive_data = normalize(wedrive_data)
    
    study_data = bus_data.reshape(-1, 100, 100, 2).astype('float32')
    study_data_label = np.array([0 for _ in range(len(study_data))])
    study_x_train, study_x_test, study_y_train, study_y_test = train_test_split(study_data, study_data_label)

    test_data = wedrive_data.reshape(-1, 100, 100, 2).astype('float32')
    shuffle_indices = np.random.permutation(np.arange(len(test_data)))
    test_data = test_data[shuffle_indices]
    test_data_label = np.array([1 for _ in range(len(test_data))])
    test_x_train, test_x_test, test_y_train, test_y_test = train_test_split(test_data[0:len(study_data)], test_data_label[0:len(study_data)])

    x_data = np.concatenate((study_x_train, test_x_train), axis=0)
    y_data = np.concatenate((study_y_train, test_y_train), axis=0)

    train_shuffle_indices = np.random.permutation(np.arange(len(x_data)))
    x_data = x_data[train_shuffle_indices]
    y_data = y_data[train_shuffle_indices]
    y_data = tf.keras.utils.to_categorical(y_data, 2)

    x_test = np.concatenate((study_x_test, test_data[len(study_data):]), axis=0)
    y_test = np.concatenate((study_y_test, test_data_label[len(study_data):]), axis=0)
    y_test = tf.keras.utils.to_categorical(y_test, 2)

    return x_data, y_data, x_test, y_test

# LGD 2020-09-10 18:57
# 모델 설정
def set_model():
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Conv2D(8, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu', input_shape=(100, 100, 2)))
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same'))
    model.add(tf.keras.layers.Conv2D(8, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu'))
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same'))
    model.add(tf.keras.layers.Conv2D(8, kernel_size=(3, 3), strides=(1, 1), padding='same', activation='relu'))
    model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same'))
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(1000, activation='relu'))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(2, activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', 
        metrics=['accuracy',
            tf.keras.metrics.Precision(name='precision'),
            tf.keras.metrics.Recall(name='recall'),
            tf.keras.metrics.FalsePositives(name='false_positives'),
            tf.keras.metrics.FalseNegatives(name='false_negatives')])

    return model

# LGD 2020-09-10 18:57
# data 불러오고 학습 실행하는 함수
# ver에 따른 모델 버전을 다르게 저장(그냥 이름을 다르게 하기 위한 용도)
def cnn_main():
    ver = "5"

    # bus npy 경로 잘보고 사용할 것
    bus_data_path = "./data/bus/npy/"
    wedrive_data_path = "./data/wedrive/npy/"

    study_data = np.load(bus_data_path)
    wedrive_data = np.load(wedrive_data_path)

    x_train, y_train, x_test, y_test = data_processing(study_data, wedrive_data)
    model = set_model()
    model.summary()
    
    model.fit(x=x_train, y=y_train, epochs=3, batch_size=64)

    eval_y = model.evaluate(x_test, y_test, batch_size=64)
    

    print(x_train.shape, x_test.shape)
    print(eval_y)
    print("f1-score", 2 * (eval_y[2] * eval_y[3]) / (eval_y[2] + eval_y[3]))

    model.save("./model/model_" + ver +".h5")

cnn_main()
