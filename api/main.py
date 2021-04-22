from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse
from sklearn.feature_extraction.text import CountVectorizer
from pandas import DataFrame
import random
import pickle  

# Import clean_data from parent directory ML-ChatApp/data/clean_data.py
import os, sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from data.clean_data import trim_data

# Initialize ML prediction server
app = Flask(__name__, static_folder="build/static", template_folder="build")
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument("Message")


class NaiveBayes(Resource):
    # INITIALIZE PRE TRAINED MODEL HERE FROM FILE
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

        return { 'Sentiment' : sentiment }


class DeepNeuralNet(Resource):
    # INITIALIZE PRE TRAINED MODEL HERE FROM FILE
    def load_model(self, path):
        return pickle.load(open(path, 'rb'))

    def __init__(self):
        # self.model = load_model("/Models/Trained_Models/DNN_Model.sav")
        pass
    
    # CALL MODEL PREDICT() here
    def predict(self, msg):
        # isPositive = self.model.predict(msg)

        # TEMPORARY RANDOM SENTIMENT until model implemented
        isPositive = random.choice([True, False])

        return isPositive

    # POST endpoint reads Message text from request body, serves response with Score
    def post(self):
        args = parser.parse_args()
        msg = args['Message']
        if(self.predict(msg)):
            sentiment = "positive"
        else:
            sentiment = "negative"

        return { 'Sentiment' : sentiment }

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
