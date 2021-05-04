# -------------------------------------------------- Import Dependencies --------------------------------------------------

from flask import Flask, render_template, jsonify
from flask_restful import Resource, Api, reqparse
from pandas import DataFrame
import pickle5 as pickle  
from clean_data import trim_data
import os
import random

# -------------------------------------------------- Setup Configuration --------------------------------------------------

# Initialize ML prediction server
app = Flask(__name__, static_folder="build/static", template_folder="build")
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument("Message")

# GCP Credentials
import googleapiclient.discovery
from google.cloud import storage
from google.api_core.client_options import ClientOptions
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"                                       
client = storage.Client()
bucket = client.get_bucket('sachatml.appspot.com')

# -------------------------------------------------- Initialization Functions --------------------------------------------------

def load_pickle(bucket_resource_path):
    pickle_file = bucket.get_blob(bucket_resource_path)
    return pickle.loads(pickle_file.download_as_string())   

# Begin initialization of resources immediately at startup
# Load files from GCP cloud storage
global DNN_VECTORIZER, NB_MODEL, NB_VECTORIZER, NB_TRANSFORMER, pad_sequences
DNN_VECTORIZER = NB_MODEL = NB_VECTORIZER = NB_TRANSFORMER = pad_sequences = None
DNN_VECTORIZER = load_pickle('DNN/lstm_vectorizer.pickle')
pad_sequences = load_pickle('DNN/pad_sequences.pickle')
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
        # sentiment = random.choice(['positive', 'negative'])
        return jsonify({ 'Sentiment' : sentiment })


class DeepNeuralNet(Resource):
    def __init__(self):
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
        # return random.choice([True, False])

        # Clean and convert message to vector 
        msg_vector = self.parse_msg(msg)

        # Generate request to GCP AI platform for prediction 
        PROJECT="sachatml"
        MODEL_NAME="SA_Chat"
        VERSION_NAME="chat_app_dnn"
        REGION="us-central1"
        
        api_endpoint = "https://{}.googleapis.com".format(REGION + '-ml')
        client_options = ClientOptions(api_endpoint=api_endpoint)
        service = googleapiclient.discovery.build('ml', 'v1', client_options=client_options)
        name = 'projects/{}/models/{}/versions/{}'.format(PROJECT, MODEL_NAME, VERSION_NAME)

        # Send request to the cloud hosted model
        response = service.projects().predict(
            name=name,
            body={'instances': msg_vector.tolist()}
        ).execute()
        if 'error' in response:
            raise RuntimeError(response['error'])

        # Using 0.5 score threshold, serve the prediction
        return response['predictions'][0][0] > 0.5

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
