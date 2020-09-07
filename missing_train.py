import pandas as pd
import os
import numpy as np
import tensorflow as tf

def train_test_split(x, y, test_size=0.2, shuffle=True, random_state=1004):
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

def normalize(data):
    data = data.astype(np.float32)
    mean = np.mean(data)
    data -= mean
    std = np.std(data)
    data /= std
    return data

def data_processing(study_data, test_data_path):
    print('study_data', study_data.shape, 'test_data_path shape:', test_data_path.shape)

    study_data = normalize(study_data)
    test_data_path = normalize(test_data_path)
    
    study_data = study_data.reshape(-1, 100, 100, 2).astype('float32')
    study_data_label = np.array([0 for _ in range(len(study_data))])
    study_x_train, study_x_test, study_y_train, study_y_test = train_test_split(study_data, study_data_label)

    test_data = test_data_path.reshape(-1, 100, 100, 2).astype('float32')
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

def cnn_main():
    cwd = os.getcwd()
    ver = "_5"
    study_data_path = cwd + \
        "\\mode\\data\\study_data\\study_data_missing" + ver +".npy"
    test_data_path = cwd + "\\mode\\data\\test_data\\wedrive_grid2.npy"

    study_data = np.load(study_data_path)
    test_data_path = np.load(test_data_path)

    x_train, y_train, x_test, y_test = data_processing(study_data, test_data_path)
    model = set_model()
    model.summary()
    '''
    model.fit(x=x_train, y=y_train, epochs=3, batch_size=64)

    eval_y = model.evaluate(x_test, y_test, batch_size=64)
    

    print(x_train.shape, x_test.shape)
    print(eval_y)
    print("f1-score", 2 * (eval_y[2] * eval_y[3]) / (eval_y[2] + eval_y[3]))

    model.save(cwd + "\\mode\\model\\model_missing" + ver +".h5")
    '''
cnn_main()
