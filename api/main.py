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

# Download model files from cloud storage
@app.before_first_request
def _load_model():
    if not (os.path.exists('tmp/GloVe_LSTM_SA_Classifier.h5') and os.path.exists('tmp/lstm_vectorizer.pickle')):
        load_files()

def load_files():
    # Load model files from cloud storage
    model_file = bucket.get_blob('DNN/GloVe_LSTM_SA_Classifier.h5')
    vectorizer_file = bucket.get_blob('DNN/lstm_vectorizer.pickle')
    model_file.download_to_filename('tmp/GloVe_LSTM_SA_Classifier.h5')
    vectorizer_file.download_to_filename('tmp/lstm_vectorizer.pickle')


class NaiveBayes(Resource):
    def __init__(self):
        self.model = pickle.load(open('Models/Trained_Models/NB/NB_Multinomial.sav', 'rb'))
        self.vectorizer = pickle.load(open("Models/Trained_Models/NB/count_vectorizer.pickle", "rb"))
        self.transformer = pickle.load(open("Models/Trained_Models/NB/TFID_Transformer.pickle", "rb"))

    # Parse message into similar format that model was trained on with movie reviews
    def parse_msg(self, msg):
        # Clean message
        data = DataFrame({ 'review' : [msg] })
        trim_data(data)
        cleaned_msg = list(data['review'])

        # turn text into count vector
        msg_counts = self.vectorizer.transform(cleaned_msg)

        # turn into tfidf vector
        return self.transformer.transform(msg_counts)  

    # POST endpoint reads Message text from request body, serves response with Score
    def post(self):
        args = parser.parse_args()
        msg = args['Message']
        msg = self.parse_msg(msg)
        sentiment = self.model.predict(msg).item(0)

        return jsonify({ 'Sentiment' : sentiment })


class DeepNeuralNet(Resource):
    def __init__(self):
        if not (os.path.exists('tmp/GloVe_LSTM_SA_Classifier.h5') and os.path.exists('tmp/lstm_vectorizer.pickle')):
            load_files()
        self.model = keras.models.load_model('tmp/GloVe_LSTM_SA_Classifier.h5')
        self.vectorizer = pickle.load(open('tmp/lstm_vectorizer.pickle', 'rb'))

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
