# -*- coding: utf-8 -*-

import sys

import json
# from collections import Counter
# from sklearn.metrics import confusion_matrix
from supporters.preprocessor import preprocessor
# from nltk.corpus import stopwords


mail_file = sys.argv[1]
words = preprocessor(mail_file)

with open("words_test.txt", "w") as info:
    info.write(json.dumps(words))    # Can't write dict to file, so write as json string

with open("dictionary") as dic:
    dictionary = json.load(dic)

print(dictionary)
