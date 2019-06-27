import spacy
import email


all_words = []


def preprocessor(mail):
    try:
        with open(mail, "r", encoding="us-ascii") as em:
            mail_body_str = em.read()
        mail_body = email.message_from_string(mail_body_str)
        find_payload(mail_body)
    except UnicodeDecodeError:
        pass
    return all_words


def find_payload(mail_body):
    if mail_body.is_multipart():
        for load in mail_body.get_payload():
            find_payload(load)
    else:
        split_payload(mail_body)


def split_payload(payload):
    content_subtype = payload.get_content_subtype()
    if content_subtype == "plain":
        content = payload.get_payload()
        if len(content) > 1000000:
            chunks, chunk_size = len(content), len(content)//999999
            for i in range(0, chunks, chunk_size):
                get_words(content[i:i+chunk_size])
        else:
            get_words(content)


def get_words(content):
    nlp = spacy.load("en_core_web_sm")
    stopWords = spacy.lang.en.stop_words.STOP_WORDS
    nlpmail = nlp(content)
    for word in nlpmail:
        lemma = word.lemma_
        lemma = lemma.lower()
        if lemma.isalpha() and len(lemma) > 2 and len(lemma) < 10 and lemma not in stopWords:
            all_words.append(lemma)
