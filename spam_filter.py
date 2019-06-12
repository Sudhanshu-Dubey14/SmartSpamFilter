# -*- coding: utf-8 -*-

import os

import json
import numpy as np
from collections import Counter
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import confusion_matrix


def make_Dictionary(train_dir):
    ''' Method to create Dictionary'''
    emails = [os.path.join(train_dir, f) for f in os.listdir(train_dir)]  # reads file names in directory
    all_words = []
    for mail in emails:
        with open(mail, "r", encoding="us-ascii") as m:
            try:
                for i, line in enumerate(m):   # enumerate reads mail and returns each line and its counter
                    if i == 2:		  # why 2? Should be >=2 if picking lines after subject.
                        words = line.split()
                        all_words += words
            except UnicodeDecodeError:
                pass

    dictionary = Counter(all_words)	  # Counts number of occurrences of words

    list_to_remove = dictionary.keys()
    improvedDict = Counter()
    i = 0
    for item in list_to_remove:
        if item.isalpha() and len(item) > 3:
            improvedDict[i] = item
            i = i+1
    improvedDict = improvedDict.most_common(3000)
    with open("dictionary", "w") as info:
        info.write("No. of Words processed: ")
        info.write('{}\n'.format(i))
    return improvedDict


def extract_features(mail_dir):
    files = [os.path.join(mail_dir, fi) for fi in os.listdir(mail_dir)]
    features_matrix = np.zeros((len(files), 3000)) 	# makes matrix of len(files)x3000 containing all 0s
    docID = 0
    print(len(files))
    for fil in files:
        try:
            with open(fil) as fi:
                for i, line in enumerate(fi):
                    if i == 2:			# why 2?
                        words = line.split()
                        for word in words:
                            if word.isalpha and len(word) > 3:
                                wordID = 0
                                for i, d in enumerate(dictionary):
                                    '''with open("dictionary_test.txt", "a") as dt:
                                        dt.write(d[1])
                                        dt.write("\t")
                                        dt.write(word)
                                        dt.write("\n")'''
                                    if d[1] == word:
                                        wordID = i
                                        features_matrix[docID, wordID] = words.count(word)
                print("Mails processed: ", docID)
                docID = docID + 1
        except UnicodeDecodeError:
            pass
    return features_matrix


# Create a dictionary of words with its frequency

train_dir = 'train-mails/'
dictionary = make_Dictionary(train_dir)
with open("dictionary", "a") as info:
    info.write(json.dumps(dictionary))    # Can't write dict to file, so write as json string

# Prepare feature vectors per training mail and its labels

train_labels = np.zeros(702)
train_labels[351:701] = 1
np.savetxt("train_labels.txt", train_labels)     # special method to save 2-D np array
train_matrix = extract_features(train_dir)
np.savetxt("train_matrix.txt", train_matrix)

# Training Naive bayes classifier

model1 = MultinomialNB()

model1.fit(train_matrix, train_labels)  # Fit Naive Bayes classifier according to train_matrix and train_labels

# Test the unseen mails for Spam

test_dir = 'test-mails/'
test_matrix = extract_features(test_dir)
np.savetxt("test_matrix.txt", test_matrix)
test_labels = np.zeros(260)
test_labels[130:260] = 1
np.savetxt("test_labels.txt", test_labels)

result1 = model1.predict(test_matrix)
np.savetxt("result1.txt", result1)


print(confusion_matrix(test_labels, result1))
