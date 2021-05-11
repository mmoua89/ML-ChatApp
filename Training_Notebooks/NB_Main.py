# Libraries
import nltk
import pandas as pd
import re
from nltk.tokenize.toktok import ToktokTokenizer
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import  MultinomialNB
from sklearn import metrics
from sklearn.feature_extraction.text import TfidfTransformer


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


def main():
    # data = pd.read_csv('./IMDB Dataset.csv')
    # trim_data(data)
    # data.to_csv('TRIM_IMDB_Dataset.csv', index=False)

    new_data = pd.read_csv('./TRIM_IMDB_Dataset.csv')


# Train data
#     movie_cv = CountVectorizer(min_df=2, max_features=3000)     # use top 3000 words only
    movie_cv = CountVectorizer(min_df=2, ngram_range=(1, 2))
    x_train, x_test, y_train, y_test = train_test_split(new_data['review'], new_data['sentiment'], test_size=.2, random_state=5)

    docs_train_counts = movie_cv.fit_transform(x_train)


# huge 40,000 docs with 3,000 unique terms
    print(docs_train_counts.shape)

# convert raw freqency counts to TF-IDF values
    movie_tfmer = TfidfTransformer()
    docs_train_tfmer = movie_tfmer.fit_transform(docs_train_counts)
    # print(docs_train_tfmer.shape)

# Test data
    docs_test_counts = movie_cv.transform(x_test)
    docs_test_tfidf = movie_tfmer.transform(docs_test_counts)

    mul = MultinomialNB()
    mul.fit(docs_train_tfmer, y_train)

    y_pred = mul.predict(docs_test_tfidf)
    score = metrics.accuracy_score(y_test, y_pred)

    print('Accuracy score of MultinomialNB: ' + str('{:04.2f}'.format(score * 100)) + '%')

    # Save trained model and vectorizer
    import pickle
    # with open('count_vectorizer.pickle', 'wb') as handle:
    #     pickle.dump(movie_cv, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('TFID_Transformer.pickle', 'wb') as handle:
        pickle.dump(movie_tfmer, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # with open('NB_Mulinomial.sav', 'wb') as handle:
    #     pickle.dump(mul, handle, protocol=pickle.HIGHEST_PROTOCOL)


# Classifier on fake movie reviews
    while True:
        reviews_new = [input("Enter a review: ")]

        if ''.join(reviews_new) == 'N' or ''.join(reviews_new) == 'n':
            return False

        reviews_new_counts = movie_cv.transform(reviews_new)  # turn text into count vector
        # print(reviews_new_counts)
        reviews_new_tfidf = movie_tfmer.transform(reviews_new_counts)  # turn into tfidf vector

        predict = mul.predict(reviews_new_tfidf)

        for review, status in zip(reviews_new, predict):
            print(review, " :: ", status)


if __name__ == '__main__':
    main()
