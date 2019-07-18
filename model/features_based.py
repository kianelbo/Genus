import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import tensorflow.python.keras as keras


class FeaturesBasedModel:
    def __init__(self, model_path=None):
        if model_path is not None:
            self.model = keras.models.load_model(model_path)
            self.encoder = pickle.load(open('save/enc_classes.pickle', 'rb'))
            self.scaler = pickle.load(open('save/feat_scaler.pickle', 'rb'))
        else:
            self.model = None
            self.encoder = LabelEncoder()
            self.scaler = StandardScaler()

    def train(self, csv_file):
        data = pd.read_csv(csv_file, encoding='ISO-8859-1')

        data.drop(['title'], axis=1, inplace=True)

        # obtaining target column and encoder
        genre_column = data['genre']
        y = self.encoder.fit_transform(genre_column)
        pickle_out = open('save/enc_classes.pickle', 'wb')
        pickle.dump(self.encoder, pickle_out)
        pickle_out.close()
        n_classes = len(self.encoder.classes_)

        # obtaining feature columns and scaler
        X = np.array(data.drop(['genre'], axis=1), dtype=float)
        X = self.scaler.fit_transform(X)
        pickle_out = open('save/feat_scaler.pickle', 'wb')
        pickle.dump(self.scaler, pickle_out)
        pickle_out.close()

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        self.model = keras.models.Sequential()
        self.model.add(keras.layers.Dense(256, activation='relu', input_shape=(X_train.shape[1],)))
        self.model.add(keras.layers.Dense(128, activation='relu'))
        self.model.add(keras.layers.Dense(64, activation='relu'))
        self.model.add(keras.layers.Dense(n_classes, activation='softmax'))
        self.model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        history = self.model.fit(X_train, y_train, epochs=20)
        print('training done')

        test_loss, test_acc = self.model.evaluate(X_test, y_test)
        print('test_acc: ', test_acc)

        self.model.save('save/fb.model')

    def predict(self, features_set):
        samples = []
        for fs in features_set:
            samples.append(fs.split(' '))

        scaled_samples = self.scaler.transform(np.array(samples, dtype=float))
        prediction = self.model.predict(scaled_samples)
        prediction = np.argmax(prediction, axis=1)
        # prediction = prediction.sum(axis=0)
        print(prediction)
        # prediction = np.argmax(prediction)
        print(self.encoder.inverse_transform(prediction))
