import nltk
from nltk.tokenize import sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords

import json
import spacy
from string import punctuation

def download():
    # nltk
    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")
    nltk.download("wordnet")
    nltk.download('stopwords')

def tokenization(text):
    return sent_tokenize(text)

def lemmatisation(text):
    lemmatizer = WordNetLemmatizer()

    # function to convert nltk tag to wordnet tag
    def nltk_tag_to_wordnet_tag(nltk_tag):
        if nltk_tag == 'NN' or nltk_tag == 'NNS':
            return wordnet.NOUN
        else:
            return None

    def lemmatize_sentence(sentence):
        # tokenize the sentence and find the POS tag for each token
        nltk_tagged = nltk.pos_tag(nltk.word_tokenize(sentence))
        # tuple of (token, wordnet_tag)
        wordnet_tagged = map(lambda x: (x[0], nltk_tag_to_wordnet_tag(x[1])), nltk_tagged)
        lemmatized_sentence = []
        for word, tag in wordnet_tagged:
            if tag:
                lemmatized_sentence.append(lemmatizer.lemmatize(word, tag))
        return " ".join(lemmatized_sentence)

    lem_sentence = []
    for s in text:
        lem_sentence.append(lemmatize_sentence(s))

    return lem_sentence

def remove_stop_words(text):
    final_sentence = []
    stop_words = set(stopwords.words('english'))
    special_chars = set(punctuation)
    special_chars.add('’')

    for s in text:
        temp = []
        for word in s.split():
            if word not in stop_words and word not in special_chars:
                temp.append(word)
        final_sentence.append(" ".join(temp))

    return final_sentence

def vectorize_words(text):
    vector_sentence = []
    nlp = spacy.load('en_core_web_lg')

    for s in text:
        vector_sentence.append(nlp(s))

    graph = {}

    for y in vector_sentence:
        for x in y:
            if not x.has_vector:
                break

            for z in y:
                if not z.has_vector or z.text == x.text:
                    break

                if x.text not in graph:
                    graph[x.text] = 0

                # TAKING AVERAGE
                graph[x.text] = float((graph[x.text] + z.similarity(x)) / 2)

    return graph

def get_key_words(vector_words_dict):
    top_words = []
    for word, similarity in vector_words_dict.items():
        top_words.append((word, similarity))

    top_words = sorted(top_words, key=lambda x: x[1], reverse=True)

    num = round(len(top_words) * 0.2)
    if num < 1:
        num = 1
    return [top_words[x][0] for x in range(num)]

def keyword_count_in_sentences(keywords, sentences):
    count = [0] * len(sentences)

    for indx in range(len(sentences)):
        for word in sentences[indx].split():
            if word.lower() in keywords:
                count[indx] += 1
    return count

def get_sentences(word_count, sent):
    vals = set(word_count)
    d = {int(k): "" for k in vals}

    for val in vals:
        res = ""
        for x in range(len(word_count)):
            if word_count[x] >= val:
                res += sent[x] + " "
        d[val] = res

    return d

def run(long_text):
    tokenized_long_text = tokenization(long_text)
    final_long_text = remove_stop_words(tokenized_long_text)
    lemmatised_text = lemmatisation(final_long_text)
    vectorised_words_dict = vectorize_words(final_long_text)
    key_words = get_key_words(vectorised_words_dict)
    sentence_importance = keyword_count_in_sentences(key_words, lemmatised_text)
    return (tokenized_long_text, sentence_importance)

def summarize(text):
    # download()
    return run(text)