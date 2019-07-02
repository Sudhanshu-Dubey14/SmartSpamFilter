# -*- coding: utf-8 -*-

##
# \file 
# \brief  Model building code
# This code builds, trains and tests a new Machine Learning model
# \author Sudhanshu Dubey
# \version    1.0
# \date   25/6/2019
# \bug No known bugs

import os

import json
import numpy as np
from collections import Counter
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import confusion_matrix
import pickle
from shutil import copyfile
from nltk.corpus import stopwords
from supporters.preprocessor import preprocessor
from supporters.features import mail_features


def make_Dictionary(train_dir):
    ##
    # \brief   Method to create Dictionary
    # \param    train_dir The directory containing mails
    # \return   dictionary The dictionary containing most common 3000 mails

    emails = [os.path.join(train_dir, f) for f in os.listdir(train_dir)]  # reads file names in directory
    all_words = []
    for mail in emails:
        words = preprocessor(mail)
        all_words += words

    dictionary = Counter(all_words)	  # Counts number of occurrences of words
    dictionary = dictionary.most_common(3000)
    return dictionary


def extract_features(mail_dir):
    ##
    # \brief    Method to extract features from all mails
    # \param    mail_dir The directory containing mails
    # \return   features_matrix A np-array containing features of all mails
    files = [os.path.join(mail_dir, fi) for fi in os.listdir(mail_dir)]
    features_matrix = np.zeros((len(files), 3000)) 	# makes matrix of len(files)x3000 containing all 0s
    docID = 0
    for fil in files:
        features = mail_features(fil)
        features_matrix[docID] = features
        docID = docID + 1
    print("Mails processed: ", docID)
    return features_matrix


stopWords = set(stopwords.words('english'))
# Create a dictionary of words with its frequency

train_dir = 'train-mails/'
dictionary = make_Dictionary(train_dir)
with open("dictionary", "w") as info:
    json.dump(dictionary, info)    # Can't write dict to file, so write as json string

# Prepare feature vectors per training mail and its labels

train_labels = np.zeros(702)
train_labels[351:701] = 1
train_matrix = extract_features(train_dir)

# Training Naive bayes classifier

model1 = MultinomialNB()

model1.fit(train_matrix, train_labels)  # Fit Naive Bayes classifier according to train_matrix and train_labels

pickle.dump(model1, open('spamfilter.sav', 'wb'))
copyfile('spamfilter.sav', 'backup/spamfilter.bk')
copyfile('dictionary', 'backup/dictionary.bk')

# Test the unseen mails for Spam

test_dir = 'test-mails/'
test_matrix = extract_features(test_dir)
test_labels = np.zeros(260)
test_labels[130:260] = 1

result1 = model1.predict(test_matrix)

print(confusion_matrix(test_labels, result1))
