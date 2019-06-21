# -*- coding: utf-8 -*-

import os
import sys

import json
import numpy as np
# from collections import Counter
from sklearn.naive_bayes import MultinomialNB
# from sklearn.metrics import confusion_matrix
import pickle
import spacy
# from nltk.corpus import stopwords


def preprocessor(mail):
    all_words = []
    nlpmail = nlp(open(mail, "r", encoding="us-ascii").read())
    for word in nlpmail:
        lemma = word.lemma_
        lemma = lemma.lower()
        if lemma.isalpha() and len(lemma) > 2 and lemma not in stopWords:
            all_words.append(lemma)
    return all_words


nlp = spacy.load("en_core_web_sm")
stopWords = spacy.lang.en.stop_words.STOP_WORDS
mail_file = sys.argv[1]
words = preprocessor(mail_file)

with open("words_test.txt", "w") as info:
    info.write(json.dumps(words))    # Can't write dict to file, so write as json string
