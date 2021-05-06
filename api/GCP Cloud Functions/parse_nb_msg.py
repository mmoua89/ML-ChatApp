import flask
import pickle5 as pickle  
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import  MultinomialNB
from google.cloud import storage

# Reinstantate trained vectorizer from cloud storage
def load_pickle(bucket_resource_path, bucket):
    pickle_file = bucket.get_blob(bucket_resource_path)
    return pickle.loads(pickle_file.download_as_string())   

"""HTTP Cloud Function.
Args:
    request (flask.Request): The request object with input message
Returns:
    The response text containing the predicted sentiment
"""
def parse_msg(request):
    # Load resources from cloud storage
    client = storage.Client()
    bucket = client.get_bucket('sachatml.appspot.com')

    NB_MODEL = load_pickle('NB/NB_Multinomial.sav', bucket)
    NB_VECTORIZER = load_pickle('NB/count_vectorizer.pickle', bucket)
    NB_TRANSFORMER = load_pickle('NB/TFID_Transformer.pickle', bucket)

    # Parse message and generate prediction
    request_json = request.get_json(silent=True)
    msg = list(request_json['Message'])
    
    msg_counts = NB_VECTORIZER.transform(msg)                       # get count vector for the cleaned message
    msg_vector = NB_TRANSFORMER.transform(msg_counts)               # turn into tfidf vector
    sentiment = NB_MODEL.predict(msg_vector).item(0)                # run prediction on msg vector

    # Return sentiment prediction as response
    return flask.jsonify({ 'Sentiment' : sentiment })