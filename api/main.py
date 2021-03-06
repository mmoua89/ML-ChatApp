# -------------------------------------------------- Import Dependencies --------------------------------------------------

from flask import Flask, render_template, jsonify
from flask_restful import Resource, Api, reqparse
from pandas import DataFrame
from google.api_core.client_options import ClientOptions
import googleapiclient.discovery
import os
import random
import json
import requests
import numpy as np

import nltk
import re
from nltk.tokenize.toktok import ToktokTokenizer
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import csv


# -------------------------------------------------- Message Cleaning Functions --------------------------------------------------

def denoise_text(text):
    soup = BeautifulSoup(text, 'html.parser')       # trim html format out
    new_text = soup.get_text()
    new_text = re.sub('\[[^]]*\]', '', new_text)    # remove between square brackets
    return new_text
def remove_special_chars(text):
    pattern = r'[^a-zA-Z\s]' #raw regex, exclude everything except letters and a space
    new_text = re.sub(pattern, '', text)
    return new_text
def stemmer(text):
    # Convert similar words to root word
    ps = nltk.porter.PorterStemmer()
    new_text = ' '.join([ps.stem(word) for word in text.split()])
    return new_text
def remove_stops(text):
    tokenizer = ToktokTokenizer()
    tokens = tokenizer.tokenize(text)
    stop_words = set(stopwords.words("english"))

    # Remove negation words from our exclude set
    for word in ['not','nor','never','no']:
        if word in stop_words: stop_words.remove(word)
    new_text = ' '.join([w for w in tokens if w not in stop_words])

    return new_text

def trim_data(data, stem_words):
    # Download necessary nltk corpus if not exist
    try:
        nltk.data.find('stopwords')
    except LookupError:
        nltk.download('stopwords')
    # convert all text in 'review' column to lowercase
    data['review'] = data['review'].str.lower()
    # Remove html strips and all noises text
    data['review'] = data['review'].apply(denoise_text)
    # Remove special chars
    data['review'] = data['review'].apply(remove_special_chars)
    # remove stopwords
    data['review'] = data['review'].apply(remove_stops)

    # Stem all word to their common word
    if(stem_words):
        data['review'] = data['review'].apply(stemmer)

# -------------------------------------------------- Setup Configuration --------------------------------------------------

# Initialize ML prediction server
app = Flask(__name__, static_folder="build/static", template_folder="build")
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument("Message")
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"                                       

# -------------------------------------------------- Utility Functions --------------------------------------------------

# Strip message of any symbols, numbers, set all to lowercase, stem all words
def clean_msg(msg, stem_words):
    data = DataFrame({ 'review' : [msg] })
    trim_data(data, stem_words)
    return list(data['review'])[0]

# Send HTTP POST request to GCP cloud utility functions
def gcp_post(resource_function, msg, key):
    url = 'https://us-central1-sachatml.cloudfunctions.net/' + resource_function
    res = requests.post(url, json={'Message' : msg}, headers={'Content-type':'application/json'})
    if(res.status_code == requests.codes.ok):
        return res.json()[key]
    else:
        return None

# -------------------------------------------------- Service Prediction Endpoints --------------------------------------------------

class NaiveBayes(Resource):
    def predict(self, msg):
        cleaned_msg = [clean_msg(msg, stem_words=True)]

        # Sent HTTP request to cloud function to predict sentiment of the message
        return gcp_post('nb_predict', cleaned_msg, 'Sentiment')

    # POST endpoint reads Message text from request body, serves response with Score
    def post(self):
        args = parser.parse_args()
        msg = args['Message']
        sentiment = self.predict(msg)
        return jsonify({ 'Sentiment' : sentiment })


class DeepNeuralNet(Resource):
    def predict(self, msg):
        # Clean and prepare message to be passed to cloud prediction
        cleaned_msg = clean_msg(msg, stem_words=False)

        # Send HTTP request to cloud function to vectorize the message
        # msg_vector = gcp_post('parse_dnn_msg', cleaned_msg, 'Message')

        # Generate request to GCP AI platform for prediction 
        PROJECT="sachatml"
        MODEL_NAME="SA_Chat"
        VERSION_NAME="stacked_lstm_unstemmed"
        REGION="us-central1"
        
        api_endpoint = "https://{}.googleapis.com".format(REGION + '-ml')
        client_options = ClientOptions(api_endpoint=api_endpoint)
        service = googleapiclient.discovery.build('ml', 'v1', client_options=client_options)
        name = 'projects/{}/models/{}/versions/{}'.format(PROJECT, MODEL_NAME, VERSION_NAME)

        # Send request to the cloud hosted model
        response = service.projects().predict(
            name=name,
            # body={'instances': msg_vector}
            body={ 'instances': [[cleaned_msg]] }
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
