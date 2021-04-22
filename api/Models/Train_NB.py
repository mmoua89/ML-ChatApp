from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import  MultinomialNB, ComplementNB, GaussianNB, BernoulliNB
from sklearn import metrics
from os import path
import numpy as np
from scipy.sparse import load_npz
import pandas as pd
import pickle

def predict_multinomialNB(x_train, y_train, x_test, y_test):
    # Train model
    mul = MultinomialNB()
    mul.fit(x_train, y_train)

    # Save model
    pickle.dump(mul, open('Trained_Models/NB_Multinomial.sav', 'wb+'))

    # Test model
    score = test(mul)
    return score


def predict_complementNB(x_train, y_train, x_test, y_test):
    # Train model
    com = ComplementNB()
    com.fit(x_train, y_train)

    # Save model
    pickle.dump(com, open('Trained_Models/NB_Complement.sav', 'wb+'))

    # Test model
    score = test(com)
    return score


def predict_bernoulliNB(x_train, y_train, x_test, y_test):
    # Train model
    ber = BernoulliNB()
    ber.fit(x_train, y_train)

    # Save model
    pickle.dump(ber, open('Trained_Models/NB_Bernoulli.sav', 'wb+'))

    # Test model
    score = test(ber)
    return score


def train():
    # Train models
    print("\nTraining and testing models . . .")
    score1 = predict_multinomialNB(x_train, y_train, x_test, y_test)
    print('Accuracy score of MultinomialNB: ' + str('{:04.2f}'.format(score1 * 100)) + '%')

    score2 = predict_complementNB(x_train, y_train, x_test, y_test)
    print('Accuracy score of ComplementNB: ' + str('{:04.2f}'.format(score2 * 100)) + '%')

    score3 = predict_bernoulliNB(x_train, y_train, x_test, y_test)
    print('Accuracy score of BernoulliNB: ' + str('{:04.2f}'.format(score3 * 100)) + '%')
    print("\nModels finished training, saving . . .")

    # gau = GaussianNB()
    # gau.fit(x_train.todense(), y_train)
    # predicted = gau.predict(x_test)
    # score = metrics.accuracy_score(predicted, y_test)
    # print('Accuracy score: ' + str('{:04.2f}'.format(score * 100)) + '%')


def test(model):
    predicted = model.predict(x_test)
    score = metrics.accuracy_score(predicted, y_test)
    return score


def load_data(data_path: str):
    # Load preprocessed data
    x_train = load_npz(data_path + '/train_and_val/word_vector.npz')
    x_test = load_npz(data_path + '/test/word_vector.npz')
    y_train = np.load(data_path + '/train_and_val/labels.npy', allow_pickle=True)
    y_test = np.load(data_path + '/test/labels.npy', allow_pickle=True)
    print("Preprocessed data has been initialized")

    return (x_train, y_train, x_test, y_test)


def load_pretrained_models():
    mul = pickle.load(open('Trained_Models/NB_Multinomial.sav', 'rb'))
    com = pickle.load(open('Trained_Models/NB_Complement.sav', 'rb'))
    ber = pickle.load(open('Trained_Models/NB_Bernoulli.sav', 'rb'))
    print("\nPretrained models have been initialized")

    return(mul, com, ber)


if __name__ == '__main__':
    # Initialize data 
    data_path =  path.abspath(path.join(__file__ ,'../../../data/'))
    x_train, y_train, x_test, y_test = load_data(data_path)

    # Train models if not already pretrained
    if(
        not path.isfile('Trained_Models/NB_Bernoulli.sav')
        or not path.isfile('Trained_Models/NB_Complement.sav')
        or not path.isfile('Trained_Models/NB_Multinomial.sav')
    ):
        train()

    # Otherwise load models
    else:
        mul, com, ber = load_pretrained_models()
        print("\nTesting . . .")
        print('Accuracy score of MultinomialNB: ' + str('{:04.2f}'.format(test(mul) * 100)) + '%')
        print('Accuracy score of MultinomialNB: ' + str('{:04.2f}'.format(test(com) * 100)) + '%')
        print('Accuracy score of MultinomialNB: ' + str('{:04.2f}'.format(test(ber) * 100)) + '%')



