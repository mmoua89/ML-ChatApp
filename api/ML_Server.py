from flask import Flask
from flask_restful import Resource, Api, reqparse

# Used to serialize/deserialize trained model (converts/loads python object to/from bytes file)
# Example: https://bit.ly/3e9islJ
import pickle  


# Initialize ML prediction server
app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
parser.add_argument("Message")


class NaiveBayes(Resource):
    # INITIALIZE PRE TRAINED MODEL HERE FROM FILE
    def load_model(self, path: str):
        return pickle.load(open(path, 'rb'))

    def __init__(self):
        # self.model = load_model("/relative/path/to/model.sav")
        pass
    
    # CALL MODEL PREDICT() here
    def predict(self, msg: str) -> float:
        # return self.model.predict(msg)

        # TEMPORARY FIXED SCORE until model implemented
        return -1

    # POST endpoint reads Message text from request body, serves response with Score
    def post(self):
        args = parser.parse_args()
        msg = args['Message']
        sentiment_score = self.predict(msg)

        return { 'Score' : sentiment_score }


class DeepNeuralNet(Resource):
    # INITIALIZE PRE TRAINED MODEL HERE FROM FILE
    def load_model(self, path: str):
        return pickle.load(open(path, 'rb'))

    def __init__(self):
        # self.model = load_model("/relative/path/to/model.sav")
        pass
    
    # CALL MODEL PREDICT() here
    def predict(self, msg: str) -> float:
        # return self.model.predict(msg)

        # TEMPORARY FIXED SCORE until model implemented
        return -1

    # POST endpoint reads Message text from request body, serves response with Score
    def post(self):
        args = parser.parse_args()
        msg = args['Message']
        sentiment_score = self.predict(msg)

        return { 'Score' : sentiment_score }


# Setup ML prediction server routing
api.add_resource(NaiveBayes, '/api/predict/NaiveBayes')
api.add_resource(DeepNeuralNet, '/api/predict/DeepNeuralNet')


# Debugging
if __name__ == '__main__':
    app.run(host="0.0.0.0", port="4000", debug=True)
