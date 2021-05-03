from flask import Flask, render_template, jsonify
from flask_restful import Resource, Api, reqparse
from sklearn.feature_extraction.text import CountVectorizer
from pandas import DataFrame
import random
import pickle  
from clean_data import trim_data

import keras
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization
from keras.preprocessing.sequence import pad_sequences


# Initialize ML prediction server
app = Flask(__name__, static_folder="build/static", template_folder="build")
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument("Message")


class NaiveBayes(Resource):
    def load_model(self, path):
        return pickle.load(open(path, 'rb'))

    def __init__(self):
        self.model = self.load_model('Models/Trained_Models/NB_Multinomial.sav')
        self.vectorizer = pickle.load(open("Models/vectorizer.pickle", "rb"))

    # Parse message into similar format that model was trained on with movie reviews
    def parse_msg(self, msg):
        # Clean message
        data = DataFrame({ 'review' : [msg] })
        trim_data(data)

        # Vectorize message
        text_counts = self.vectorizer.fit_transform(data['review'])

        # Reshape for prediction, size of single message in training data vector
        text_counts.resize((1, 2964871))            
        return text_counts

    # POST endpoint reads Message text from request body, serves response with Score
    def post(self):
        args = parser.parse_args()
        msg = args['Message']
        msg = self.parse_msg(msg)
        sentiment = self.model.predict(msg)[0]

        return jsonify({ 'Sentiment' : sentiment })


class DeepNeuralNet(Resource):
    def __init__(self):
        self.model = keras.models.load_model('Models/Trained_Models/GloVe_LSTM_SA_Classifier.h5')
        self.vectorizer = pickle.load(open('Models/lstm_vectorizer.pickle', 'rb'))

    def vectorize(self, data):
        vectorized_txt = self.vectorizer.texts_to_sequences(data['review'].values)
        vectorized_txt = pad_sequences(vectorized_txt, padding='post', maxlen=100)
        return vectorized_txt

    def parse_msg(self, msg):
        # Clean message
        data = DataFrame({ 'review' : [msg] })
        trim_data(data)
        return self.vectorize(data)
    
    # CALL MODEL PREDICT() here
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
