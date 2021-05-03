from flask import Flask, render_template, jsonify
from flask_restful import Resource, Api, reqparse
from sklearn.feature_extraction.text import CountVectorizer
from pandas import DataFrame
import random
import pickle  
from clean_data import trim_data
import os
import keras
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization
from keras.preprocessing.sequence import pad_sequences


from google.cloud import storage
from pickle_model import make_picklable



# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"
# client = storage.Client()
# bucket = client.get_bucket('sachatml.appspot.com')

# model_file = bucket.get_blob('DNN/GloVe_LSTM_SA_Classifier.h5')

make_picklable()
with open('GloVe_LSTM_SA_Classifier.sav', 'rb') as handle:
    model = pickle.load(handle)

print(model.summary())