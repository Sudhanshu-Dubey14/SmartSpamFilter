import spacy


def preprocessor(mail):
    all_words = []
    nlp = spacy.load("en_core_web_sm")
    stopWords = spacy.lang.en.stop_words.STOP_WORDS
    nlpmail = nlp(open(mail, "r", encoding="us-ascii").read())
    for word in nlpmail:
        lemma = word.lemma_
        lemma = lemma.lower()
        if lemma.isalpha() and len(lemma) > 2 and lemma not in stopWords:
            all_words.append(lemma)
    return all_words
