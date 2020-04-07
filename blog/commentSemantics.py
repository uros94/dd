import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import _pickle as pickle
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

# load the model from disk
model = pickle.load(open(os.path.join(script_dir,"model.pickle"), "rb"))
vectorizer = pickle.load(open(os.path.join(script_dir,"vectorizer.pickle"), "rb"))

def classify(sentence, show_details=False):
    vector = vectorizer.transform([sentence]).toarray()
    #y_pred = model.predict(vector)
    y_prob = model.predict_proba(vector)
    if y_prob[0][0]>0.7:
        return -1
    elif y_prob[0][1]>0.6:
        return 1
    else:
        return 0
