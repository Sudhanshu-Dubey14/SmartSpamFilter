# -*- coding: utf-8 -*-

import os

import chardet
import numpy as np
from collections import Counter
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import confusion_matrix


def make_Dictionary(train_dir):
    ''' Method to create Dictionary'''
    emails = [os.path.join(train_dir, f) for f in os.listdir(train_dir)]  # reads file names in directory and appends it with directory name
    all_words = []
    for mail in emails:
        with open(mail) as m:
            mailstr = str(m)
            charset=chardet.detect(mailstr)
            for i,line in enumerate(m):   # enumerate reads mail and returns each line and its counter
                if i == 2:		  # why 2? Should be >=2 if picking lines after subject.
                    words = line.split()
                    all_words += words

    dictionary = Counter(all_words)	# Counts number of occurrences of words

    list_to_remove = dictionary.keys()
    for item in list_to_remove:
        if item.isalpha() == False:
            del dictionary[item]
        elif len(item) == 1:
            del dictionary[item]
    dictionary = dictionary.most_common(3000)
    return dictionary

def extract_features(mail_dir):
    files = [os.path.join(mail_dir,fi) for fi in os.listdir(mail_dir)]
    features_matrix = np.zeros((len(files),3000)) 	#makes matrix of len(files) or 3000 containing all 0s
    docID = 0;
    for fil in files:
      with open(fil) as fi:
        for i,line in enumerate(fi):
          if i == 2:			#why 2?
            words = line.split()
            for word in words:
              wordID = 0
              for i,d in enumerate(dictionary):
                if d[0] == word:
                  wordID = i
                  features_matrix[docID,wordID] = words.count(word)
        docID = docID + 1
    return features_matrix

# Create a dictionary of words with its frequency

train_dir = 'train-mails/'
dictionary = make_Dictionary(train_dir)

# Prepare feature vectors per training mail and its labels

train_labels = np.zeros(702)
train_labels[351:701] = 1
train_matrix = extract_features(train_dir)

# Training Naive bayes classifier

model1 = MultinomialNB()

model1.fit(train_matrix,train_labels)	#Fit Naive Bayes classifier according to train_matrix and train_labels

# Test the unseen mails for Spam

test_dir = 'test-mails/'
test_matrix = extract_features(test_dir)
test_labels = np.zeros(260)
test_labels[130:260] = 1

result1 = model1.predict(test_matrix)

print(confusion_matrix(test_labels,result1))
