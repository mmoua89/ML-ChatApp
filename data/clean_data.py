'''
Clean dataset by remoiving noise from html, symbols, stop words
Stem words to their root word using nltk
Dataset: http://ai.stanford.edu/~amaas/data/sentiment/
'''

# Libraries
import nltk
import pandas as pd
import re
from nltk.tokenize.toktok import ToktokTokenizer
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import csv

# ----------------------------------------------{
def denoise_text(text):
    soup = BeautifulSoup(text, 'html.parser')       # trim html format out
    new_text = soup.get_text()
    new_text = re.sub('\[[^]]*\]', '', new_text)    # remove between square brackets
    return new_text
# ----------------------------------------------}


def remove_special_chars(text):
    pattern = r'[^a-zA-Z0-9\s]'
    # pattern = r'[^a-zA-Z\s]' #raw regex, exclude everything except letters and a space
    new_text = re.sub(pattern, '', text)
    return new_text


def stemmer(text):
    """
    Convert similar words to root word
    :param text:
    :return:
    """
    ps = nltk.porter.PorterStemmer()
    new_text = ' '.join([ps.stem(word) for word in text.split()])
    return new_text


def remove_stops(text):
    tokenizer = ToktokTokenizer()

    tokens = tokenizer.tokenize(text)

    stop_words = set(stopwords.words("english"))

    new_text = ' '.join([w for w in tokens if w not in stop_words])
    return new_text


def trim_data(data):
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

    # Stem all word to their common word
    data['review'] = data['review'].apply(stemmer)

    # remove stopwords
    data['review'] = data['review'].apply(remove_stops)



if __name__ == '__main__':

    # Read raw dataset
    data = pd.read_csv('IMDB_Dataset.csv')

    # Clean and save data
    trim_data(data)
    data.to_csv('Cleaned_IMDB_Dataset.csv', index=False)