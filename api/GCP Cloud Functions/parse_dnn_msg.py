import flask
import pickle5 as pickle  
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization
from keras.preprocessing.sequence import pad_sequences
from google.cloud import storage

# Reinstantate trained vectorizer from cloud storage
def load_pickle(bucket_resource_path, bucket):
    pickle_file = bucket.get_blob(bucket_resource_path)
    return pickle.loads(pickle_file.download_as_string())   

"""HTTP Cloud Function.
Args:
    request (flask.Request): The request object with input message
Returns:
    The parsed response text
"""
def parse_msg(request):
    # Load resources from cloud storage
    client = storage.Client()
    bucket = client.get_bucket('sachatml.appspot.com')
    DNN_VECTORIZER = load_pickle('DNN/lstm_vectorizer.pickle', bucket)
    
    request_json = request.get_json(silent=True)
    msg = request_json['Message']
    vectorized_txt = DNN_VECTORIZER.texts_to_sequences(data['review'].values)
    vectorized_txt = pad_sequences(vectorized_txt, padding='post', maxlen=100)

    return flask.jsonify({ 'Message' : vectorized_txt.tolist() })