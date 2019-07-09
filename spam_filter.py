# -*- coding: utf-8 -*-

##
# \file
# \brief  Model building code
# \details This code builds and trains a new Machine Learning model
# \author Sudhanshu Dubey
# \version    1.1
# \date   9/7/2019
# \param    ham_dir Directory containing ham mails for training
# \param    spam_dir    Directory containing spam mails for training
# \bug No known bugs (untested)

import os
import sys

import json
import numpy as np
from collections import Counter
from sklearn.naive_bayes import MultinomialNB
import pickle
from shutil import copyfile
import spacy
import email
from bs4 import BeautifulSoup


def make_Dictionary(emails):
    ##
    # \brief   Method to create Dictionary
    # \param    train_dir The directory containing mails
    # \return   dictionary The dictionary containing most common 3000 words

    all_words = []
    for mail in emails:
        words = preprocessor(mail)
        all_words += words

    dictionary = Counter(all_words)	  # Counts number of occurrences of words
    dictionary = dictionary.most_common(dic_size)
    return dictionary


def extract_features(files):
    ##
    # \brief    Method to extract features from all mails
    # \param    mail_dir The directory containing mails
    # \return   features_matrix A np-array containing features of all mails
    features_matrix = np.zeros((len(files), dic_size))
    docID = 0
    for fil in files:
        features = mail_features(fil)
        features_matrix[docID] = features
        docID = docID + 1
    print("Mails processed: ", docID)
    return features_matrix


def mail_features(mail):
    ##
    # \brief   Method to find features of a single mail
    # \param    mail The address of mail
    # \return   features_matrix: The features of a single mail

    features_matrix = np.zeros((1, 3000)) 	# makes matrix of 1x3000 containing all 0s
    words = preprocessor(mail)
    for word in words:
        wordID = 0
        for i, d in enumerate(dictionary):
            if word == d[0]:
                wordID = i
                features_matrix[0, wordID] = words.count(word)
    return features_matrix


def preprocessor(mail):
    ##
    # \brief   Method to pre-process the mails
    # \param    mail The address of mail
    # \return   all_words: List of all words in mail

    all_words = []
    try:
        with open(mail, "r", encoding="us-ascii") as em:
            mail_body_str = em.read()
        mail_body = email.message_from_string(mail_body_str)
        find_payload(mail_body, all_words)
    except UnicodeDecodeError:
        pass
    print("Keywords extracted from " + mail)
    return all_words


def find_payload(mail_body, all_words):
    ##
    # \brief   Method to recursively find single part payloads
    # \param    mail_body   The complete mail body
    # \param    all_words   List of all words in the mail
    # \return   Nothing

    if mail_body.is_multipart():
        for load in mail_body.get_payload():
            find_payload(load, all_words)
    else:
        split_payload(mail_body, all_words)


def split_payload(payload, all_words):
    ##
    # \brief   Method to split the large payloads into smaller chunks
    # \param    payload The complete payload
    # \param    all_words   List of all words in the mail
    # \return   Nothing

    content_subtype = payload.get_content_subtype()
    if content_subtype == "plain":
        content = payload.get_payload()
        if len(content) > 1000000:
            chunks, chunk_size = len(content), len(content)//999999
            for i in range(0, chunks, chunk_size):
                get_words_plain(content[i:i+chunk_size], all_words)
        else:
            get_words_plain(content, all_words)
    elif content_subtype == "html":
        content = payload.get_payload()
        if len(content) > 1000000:
            chunks, chunk_size = len(content), len(content)//999999
            for i in range(0, chunks, chunk_size):
                get_words_html(content[i:i+chunk_size], all_words)
        else:
            get_words_html(content, all_words)


def get_words_plain(content, all_words):
    ##
    # \brief   Method to get words out of plain text content
    # \param    content Plain text content
    # \param    all_words   List of all words in the mail
    # \return   Nothing

    nlpmail = nlp(content)
    for word in nlpmail:
        lemma = word.lemma_
        lemma = lemma.lower()
        if lemma.isalpha() and len(lemma) > 2 and len(lemma) < 10 and lemma not in stopWords:
            all_words.append(lemma)


def get_words_html(content, all_words):
    ##
    # \brief   Method to get words out of html content
    # \param    content The html content
    # \param    all_words   List of all words in the mail
    # \return   Nothing

    pure_html = BeautifulSoup(content, features="lxml")
    for script in pure_html(["script", "style"]):
        script.extract()
    pure_text = pure_html.get_text()
    lines = (line.strip() for line in pure_text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    pure_text = '\n'.join(chunk for chunk in chunks if chunk)
    nlpmail = nlp(pure_text)
    for word in nlpmail:
        lemma = word.lemma_
        lemma = lemma.lower()
        if lemma.isalpha() and len(lemma) > 2 and len(lemma) < 20 and lemma not in stopWords:
            all_words.append(lemma)


nlp = spacy.load("en_core_web_sm")
stopWords = spacy.lang.en.stop_words.STOP_WORDS

# Create a dictionary of words with its frequency

ham_dir = sys.argv[1]
ham_mails = [os.path.join(ham_dir, f) for f in os.listdir(ham_dir)]  # reads file names in ham directory
ham_size = len(ham_mails)

spam_dir = sys.argv[2]
spam_mails = [os.path.join(spam_dir, f) for f in os.listdir(spam_dir)]  # reads file names in spam directory
spam_size = len(spam_mails)

all_mails = ham_mails + spam_mails
all_size = len(all_mails)

dic_size = 3000
dictionary = make_Dictionary(all_mails)
with open("dictionary", "w") as info:
    json.dump(dictionary, info)    # Can't write list to file, so write as json string

# Prepare feature vectors per training mail and its labels

mail_labels = np.zeros(all_size)
mail_labels[ham_size:all_size] = 1
mail_feature_matrix = extract_features(all_mails)

# Training Naive bayes classifier

ML_model = MultinomialNB()

ML_model.fit(mail_feature_matrix, mail_labels)  # Fit Naive Bayes classifier according to train_matrix and train_labels

pickle.dump(ML_model, open('spamfilter.sav', 'wb'))
copyfile('spamfilter.sav', 'backup/spamfilter.bk')
copyfile('dictionary', 'backup/dictionary.bk')
