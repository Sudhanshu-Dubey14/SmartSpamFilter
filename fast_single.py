# -*- coding: utf-8 -*-


##
# \file
# \brief  Continuous Single Mail Processing Code
# \details  This code loads the modules, continuously reads address of mails from log file and processes them.
# \author Sudhanshu Dubey
# \version    1.0
# \date   3/7/2019
# \params   logfile_location The location of log file.
# \bug No known bugs

import os
import sys
import time
from datetime import datetime

import pickle
import numpy as np
import json
import spacy
import email
from bs4 import BeautifulSoup
import shutil


def predict(mail_file):
    ##
    # \brief   Method to predict result of a single mail
    # \param    mail_file The address of mail
    # \return   result: The result of a mail in binary

    features_matrix = mail_features(mail_file)
    result = ml_model.predict(features_matrix)
    return result


def mail_features(mail):
    ##
    # \brief   Method to find features of a single mail
    # \param    mail The address of mail
    # \return   features_matrix: The features of a single mail

    features_matrix = np.zeros((1, dic_size))
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


def get_spam_address(mail_address):
    directory, filename = mail_address.rsplit('/', 1)
    spam_dir = "/var/mail/folder/spam"
    full_spam_address = spam_dir + "/" + filename
    return full_spam_address


nlp = spacy.load("en_core_web_sm")
stopWords = spacy.lang.en.stop_words.STOP_WORDS
with open("dictionary") as dic:
    dictionary = json.load(dic)
dic_size = 3000
ml_model = pickle.load(open('spamfilter.sav', 'rb'))

"""Read the mail name from a logfile continuously"""
logfile_location = sys.argv[1]
logfile = open(logfile_location, "r")
logfile_ino = os.fstat(logfile.fileno()).st_ino
while True:
    while True:
        mail = logfile.readline()
        if mail == "":
            break
        startTime = datetime.now()
        result = predict(mail.rstrip())
        endTime = datetime.now()
        processTime = endTime - startTime
        with open("spamfilter.log", "a") as fil:
            if result == 1:
                shutil.move(mail.rstrip(), get_spam_address(mail.rstrip()))
                fil.write(mail + " is a spam!!!\t Found in:" + str(processTime) + "\n")
            elif result == 0:
                fil.write(mail + " is a normal mail.\t Found in:" + str(processTime) + "\n")
            else:
                fil.write("Something went wrong with " + mail + "\t Found in:" + str(processTime) + "\n")
    try:
        if os.stat(logfile_location).st_ino != logfile_ino:
            new = open(logfile_location, "r")
            logfile.close()
            logfile = new
            logfile_ino = os.fstat(logfile.fileno()).st_ino
            continue
    except IOError:
        pass
    time.sleep(1)
