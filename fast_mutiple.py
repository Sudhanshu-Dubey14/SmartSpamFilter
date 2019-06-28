import os
import pickle
import numpy as np
import json
import spacy
import email
from bs4 import BeautifulSoup


def multiple(mail_dir):
    i = 0
    emails = [os.path.join(mail_dir, f) for f in os.listdir(mail_dir)]  # reads file names in directory
    with open("fastresult.txt", "w") as res:
        for mail in emails:
            print(mail + " is processing...")
            result = predict(mail)
            if result == 1:
                res.write(mail + " is a spam!!!\n")
            elif result == 0:
                res.write(mail + " is normal mail.\n")
            else:
                res.write("something went wrong for " + mail + "\n")
            i = i + 1
            print(i)
            print(mail + " is processesd.")


def predict(mail_file):
    features_matrix = mail_features(mail_file)
    result = ml_model.predict(features_matrix)
    return result


def mail_features(mail):
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
    if mail_body.is_multipart():
        for load in mail_body.get_payload():
            find_payload(load, all_words)
    else:
        split_payload(mail_body, all_words)


def split_payload(payload, all_words):
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
    nlpmail = nlp(content)
    for word in nlpmail:
        lemma = word.lemma_
        lemma = lemma.lower()
        if lemma.isalpha() and len(lemma) > 2 and len(lemma) < 10 and lemma not in stopWords:
            all_words.append(lemma)


def get_words_html(content, all_words):
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
with open("dictionary") as dic:
    dictionary = json.load(dic)
ml_model = pickle.load(open('spamfilter.sav', 'rb'))
multiple('a/')
