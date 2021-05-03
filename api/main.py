# -------------------------------------------------- Import Dependencies --------------------------------------------------

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

from tensorflow.python.lib.io.file_io import FileIO
import contextlib
import h5py

# -------------------------------------------------- Setup Configuration --------------------------------------------------

# Initialize ML prediction server
app = Flask(__name__, static_folder="build/static", template_folder="build")
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument("Message")

# GCP Credentials
from google.cloud import storage
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"                                       
client = storage.Client()
bucket = client.get_bucket('sachatml.appspot.com')

# -------------------------------------------------- Initialization Functions --------------------------------------------------

def load_keras_model(gs_resource_path):
    model_file = FileIO(gs_resource_path, mode='rb')
    file_access_property_list = h5py.h5p.create(h5py.h5p.FILE_ACCESS)
    file_access_property_list.set_fapl_core(backing_store=False)
    file_access_property_list.set_file_image(model_file.read())  
    file_id_args = {
        'fapl': file_access_property_list,
        'flags': h5py.h5f.ACC_RDONLY,
        'name': b'this should never matter',
    }
    h5_file_args = {
        'backing_store': False,
        'driver': 'core',
        'mode': 'r',
    }
    # Create temporary "file" in RAM to load (since Google AppEngine does not allow Read/Write)
    with contextlib.closing(h5py.h5f.open(**file_id_args)) as file_id:
        with h5py.File(file_id, **h5_file_args) as h5_file:
            return keras.models.load_model(h5_file)

def load_pickle(bucket_resource_path):
    pickle_file = bucket.get_blob(bucket_resource_path)
    return pickle.loads(pickle_file.download_as_string())   

# Begin initialization of resources immediately at startup
# Load files from GCP cloud storage
global DNN_MODEL, DNN_VECTORIZER, NB_MODEL, NB_VECTORIZER, NB_TRANSFORMER
DNN_MODEL = load_keras_model('gs://sachatml.appspot.com/DNN/GloVe_LSTM_SA_Classifier.h5')
DNN_VECTORIZER = load_pickle('DNN/lstm_vectorizer.pickle')
NB_MODEL = load_pickle('NB/NB_Multinomial.sav')
NB_VECTORIZER = load_pickle('NB/count_vectorizer.pickle')
NB_TRANSFORMER = load_pickle('NB/TFID_Transformer.pickle')

# -------------------------------------------------- Service Prediction Endpoints --------------------------------------------------

class NaiveBayes(Resource):
    def __init__(self):
        self.model = NB_MODEL
        self.vectorizer = NB_VECTORIZER
        self.transformer = NB_TRANSFORMER

    def vectorize(self, data):
        # turn text into count vector
        msg_counts = self.vectorizer.transform(data)
        # turn into tfidf vector
        return self.transformer.transform(msg_counts)  

    # Parse message into similar format that model was trained on with movie reviews
    def parse_msg(self, msg):
        # Clean message
        data = DataFrame({ 'review' : [msg] })
        trim_data(data)
        cleaned_msg = list(data['review'])
        return self.vectorize(cleaned_msg)

    def predict(self, msg):
        msg_vector = self.parse_msg(msg)
        return self.model.predict(msg_vector).item(0)

    # POST endpoint reads Message text from request body, serves response with Score
    def post(self):
        args = parser.parse_args()
        msg = args['Message']
        sentiment = self.predict(msg)
    
        return jsonify({ 'Sentiment' : sentiment })


class DeepNeuralNet(Resource):
    def __init__(self):
        self.model = DNN_MODEL
        self.vectorizer = DNN_VECTORIZER

    # Convert message to pass to model
    def vectorize(self, data):
        vectorized_txt = self.vectorizer.texts_to_sequences(data['review'].values)
        vectorized_txt = pad_sequences(vectorized_txt, padding='post', maxlen=100)
        return vectorized_txt

    # Clean message
    def parse_msg(self, msg):
        data = DataFrame({ 'review' : [msg] })
        trim_data(data)
        return self.vectorize(data)
    
    def predict(self, msg):
        msg_vector = self.parse_msg(msg)
        isPositive = self.model.predict(msg_vector) > 0.5
        return isPositive

    # POST endpoint reads Message text from request body, serves response with Score
    def post(self):
        args = parser.parse_args()
        msg = args['Message']
        if(self.predict(msg)):
            sentiment = "positive"
        else:
            sentiment = "negative"

        return jsonify({ 'Sentiment' : sentiment })


# -------------------------------------------------- Server Routing Configuration --------------------------------------------------

# Deployed production route, DO NOT use for development 
# (cd to react_frontend and run yarn start and yarn start-api from two terminals instead)
# React app is available on localhost:3000, API calls are configured to proxy to localhost:5000 automatically
@app.route("/")
def index():
    return render_template('index.html')

# Setup ML prediction server routing
api.add_resource(NaiveBayes, '/api/predict/NaiveBayes')
api.add_resource(DeepNeuralNet, '/api/predict/DeepNeuralNet')

# Setup local dev debugging
if __name__ == '__main__':
    app.run(host="0.0.0.0", port="4000", debug=True)
