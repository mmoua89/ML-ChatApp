import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews as mr
import pandas as pd
import nltk
# nltk.download()


def extract_features(word_list):
    return dict([(word, True) for word in word_list])


def prediction(classifier):
    while True:
        user_input = input("Please enter a message to analysis: ")

        if user_input == 'N' or user_input == 'n':
            return False

        print("Review:", user_input)
        probdist = classifier.prob_classify(extract_features(user_input.split()))
        pred_sentiment = probdist.max()

        print("Predicted sentiment: ", pred_sentiment)
        print("Probability: ", round(probdist.prob(pred_sentiment), 2))
        print()


def main():
    # Load positive and negative reviews
    positive_fileids = mr.fileids('pos')
    negative_fileids = mr.fileids('neg')

    features_positive = [(extract_features(mr.words(fileids=[f])), 'Positive') for f in positive_fileids]
    features_negative = [(extract_features(mr.words(fileids=[f])), 'Negative') for f in negative_fileids]

    # Split the data into train and test (80/20)
    threshold_factor = 0.8
    threshold_positive = int(threshold_factor * len(features_positive))
    threshold_negative = int(threshold_factor * len(features_negative))

    features_train = features_positive[:threshold_positive] + features_negative[:threshold_negative]
    features_test = features_positive[threshold_positive:] + features_negative[threshold_negative:]

    classifier = NaiveBayesClassifier.train(features_train)

    # To predict <<<<<<<<<<<<<<<
    prediction(classifier)


if __name__ == '__main__':
    main()
