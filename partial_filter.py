import os
import pickle
import numpy as np
import json
import spacy
import email
from bs4 import BeautifulSoup
import sys
from collections import Counter


def update_Dictionary(emails):
    """ Method to update Dictionary"""
    all_words = []
    i = 0
    for mail in emails:
        i = i + 1
        print("mail id: " + str(i))
        words = preprocessor(mail)
        all_words += words

    new_dictionary = Counter(all_words)	  # Counts number of occurrences of words
    for i, d in enumerate(dictionary):
        new_dictionary.update({d[0]: d[1]})
    new_dictionary = new_dictionary.most_common(4000)
    return new_dictionary


def extract_features(files):
    """ Method to extract features from all mails"""
    features_matrix = np.zeros((len(files), 4000)) 	# makes matrix of len(files)x3000 containing all 0s
    docID = 0
    for fil in files:
        print(fil + "is in process...")
        features = mail_features(fil)
        features_matrix[docID] = features
        docID = docID + 1
        print(str(docID) + ": " + fil + " is processed.")
    print("Mails processed: ", docID)
    return features_matrix


def mail_features(mail):
    features_matrix = np.zeros((1, 4000)) 	# makes matrix of 1x3000 containing all 0s
    words = preprocessor(mail)
    for word in words:
        wordID = 0
        for i, d in enumerate(new_dictionary):
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
    print("Keywords extracted from " + mail)
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


'''Load SpaCy NLP modules'''
nlp = spacy.load("en_core_web_sm")
stopWords = spacy.lang.en.stop_words.STOP_WORDS

'''Load old dictionary'''
with open("dictionary") as dic:
    dictionary = json.load(dic)

'''Load old ML model'''
ml_model = pickle.load(open('spamfilter.sav', 'rb'))

'''Read command line argument'''
directory = sys.argv[1]

emails = [os.path.join(directory, f) for f in os.listdir(directory)]  # reads file names in directory
no_emails = len(emails)

'''Produce and save new dictionary'''
new_dictionary = update_Dictionary(emails)
print("Dictionary Updated!")
with open("dictionary", "w") as dic:
    json.dump(new_dictionary, dic)

'''Find new features'''
new_features = extract_features(emails)
print("New features obtained")
new_train_labels = np.zeros(no_emails)
new_train_labels[0:no_emails] = 1

ml_model.partial_fit(new_features, new_train_labels)
pickle.dump(ml_model, open('spamfilter.sav', 'wb'))
print("ML Model updated!")

# multiple(directory)
