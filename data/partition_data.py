'''
Partition and vectorized cleaned dataset into:
    - 70% Training data (35,000 reviews)
    - 10% Validation data (5,000 reviews)
    - 20% Testing data (10,000 reviews)
Dataset: http://ai.stanford.edu/~amaas/data/sentiment/
'''

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from pandas import read_csv
from numpy import save
from scipy.sparse import save_npz
from copy import deepcopy
from os import path
import pickle

# 50,000 move reviews with { positive, negative } labels
data = read_csv('Cleaned_IMDB_Dataset.csv')

# Learn vocabulary dictionary of 1-grams 
# and also include 2-grams for words like 
cv = CountVectorizer(ngram_range=(1, 2))
text_counts = cv.fit_transform(data['review'])

# Split entire dataset into 80% train, 20% test
x_train, x_test, y_train, y_test = train_test_split(text_counts, data['sentiment'], test_size=.2, random_state=5)

# Save additional partition of just the 80% training, 20% testing without any val set
x_train_and_val = deepcopy(x_train)
y_train_and_val = deepcopy(y_train)

# Split from the 10% of the entire dataset into validation (from the partitioned training data)
# 0.125 * 0.8 = 0.1
x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.125, random_state=5) 

# Write the preprocessed data
save_npz('val/word_vector.npz', x_val)
save('val/labels.npy', y_val)

save_npz('test/word_vector.npz', x_test)
save('test/labels.npy', y_test)

save_npz('train/word_vector.npz', x_train)
save('train/labels.npy', y_train)

save_npz('train_and_val/word_vector.npz', x_train_and_val)
save('train_and_val/labels.npy', y_train_and_val)

# Save vectorizer to parse user messages later
vectorizer_path = path.abspath(path.join(__file__ ,'../../api/Models'))
pickle.dump(cv, open(vectorizer_path + "/vectorizer.pickle", "wb+"))
