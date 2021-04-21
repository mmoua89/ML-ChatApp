# Libraries
import nltk
import pandas as pd
import re
from nltk.tokenize.toktok import ToktokTokenizer
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import csv

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import  MultinomialNB, ComplementNB, GaussianNB, BernoulliNB
from sklearn import metrics


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


def predit_multinomialNB(x_train, y_train, x_test, y_test):
    mul = MultinomialNB()
    mul.fit(x_train, y_train)
    predicted = mul.predict(x_test)
    score = metrics.accuracy_score(predicted, y_test)
    return score


def predit_complementNB(x_train, y_train, x_test, y_test):
    com = ComplementNB()
    com.fit(x_train, y_train)
    predicted = com.predict(x_test)
    score = metrics.accuracy_score(predicted, y_test)
    return score


def predit_bernoulliNB(x_train, y_train, x_test, y_test):
    ber = BernoulliNB()
    ber.fit(x_train, y_train)
    predicted = ber.predict(x_test)
    score = metrics.accuracy_score(predicted, y_test)
    return score


def main():
    # data = pd.read_csv('./IMDB Dataset.csv')
    # trim_data(data)
    # data.to_csv('TRIM_IMDB_Dataset.csv', index=False)

    new_data = pd.read_csv('./TRIM_IMDB_Dataset.csv')
    # print(new_data.head(5))

    cv = CountVectorizer(ngram_range=(1, 2))
    text_counts = cv.fit_transform(new_data['review'])
    x_train, x_test, y_train, y_test = train_test_split(text_counts, new_data['sentiment'], test_size=.2, random_state=5)

    score1 = predit_multinomialNB(x_train, y_train, x_test, y_test)
    print('Accuracy score of MultinomialNB: ' + str('{:04.2f}'.format(score1 * 100)) + '%')

    score2 = predit_complementNB(x_train, y_train, x_test, y_test)
    print('Accuracy score of ComplementNB: ' + str('{:04.2f}'.format(score2 * 100)) + '%')

    score3 = predit_bernoulliNB(x_train, y_train, x_test, y_test)
    print('Accuracy score of BernoulliNB: ' + str('{:04.2f}'.format(score3 * 100)) + '%')

    # gau = GaussianNB()
    # gau.fit(x_train.todense(), y_train)
    # predicted = gau.predict(x_test)
    # score = metrics.accuracy_score(predicted, y_test)
    # print('Accuracy score: ' + str('{:04.2f}'.format(score * 100)) + '%')


if __name__ == '__main__':
    main()


