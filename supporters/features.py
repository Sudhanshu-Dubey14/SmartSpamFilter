from supporters.preprocessor import preprocessor
import json
import numpy as np


def mail_features(mail):
    features_matrix = np.zeros((1, 3000)) 	# makes matrix of 1x3000 containing all 0s
    with open("dictionary") as dic:
        dictionary = json.load(dic)
    words = preprocessor(mail)
    for word in words:
        wordID = 0
        for i, d in enumerate(dictionary):
            if word == d[0]:
                wordID = i
                features_matrix[0, wordID] = words.count(word)
    return features_matrix
