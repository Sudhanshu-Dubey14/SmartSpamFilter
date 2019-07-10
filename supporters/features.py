from supporters.preprocessor import preprocessor
import json
import numpy as np

dic_size = 3000


def mail_features(mail):
    features_matrix = np.zeros((1, dic_size))
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
