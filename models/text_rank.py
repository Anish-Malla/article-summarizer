import nltk
from nltk.tokenize import sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords

import spacy
from string import punctuation

def download():
    # nltk
    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")
    nltk.download("wordnet")
    nltk.download('stopwords')

def tokenization(text):
    """
    Unedited text converted to a list of sentences
    """
    return sent_tokenize(text)

def lemmatisation(text):
    """
    Each sentence lemmatized
    """
    lemmatizer = WordNetLemmatizer()

    def nltk_tag_to_wordnet_tag(nltk_tag):
        """
        Converts NLTK tag to wordnet tag
        """
        # Only consider of its a noun
        if nltk_tag == 'NN' or nltk_tag == 'NNS':
            return wordnet.NOUN
        else:
            return None

    def lemmatize_sentence(sentence):
        """
        Lemmatizes a specific sentence
        """
        # tokenize sentence (getting each word) and getting its POS tag
        nltk_tagged = nltk.pos_tag(nltk.word_tokenize(sentence))
        # tuple of (token, wordnet_tag)
        wordnet_tagged = map(lambda x: (x[0], nltk_tag_to_wordnet_tag(x[1])), nltk_tagged)
        lemmatized_sentence = []

        for word, tag in wordnet_tagged:
            if tag:
                # only if its a noun
                lemmatized_sentence.append(lemmatizer.lemmatize(word, tag))

        return " ".join(lemmatized_sentence)

    lem_sentence = []
    # Iterate through each sentence and run it through lemmatizer
    for s in text:
        lem_sentence.append(lemmatize_sentence(s))

    return lem_sentence

def remove_stop_words(text):
    """
    Given sentences the stop words and punctuations are removed
    """
    final_sentence = []
    stop_words = set(stopwords.words('english'))
    special_chars = set(punctuation)
    special_chars.add('’')

    # Iterate through each word in each of the sentences and remove the stop words
    for s in text:
        temp = []
        for word in s.split():
            if word not in stop_words and word not in special_chars:
                temp.append(word)
        final_sentence.append(" ".join(temp))

    return final_sentence

def vectorize_words(text):
    """
    Converting each word to a vector and returns dictionary with a word and its average similarity value
    """
    vector_sentence = []
    nlp = spacy.load('en_core_web_md')

    # convert to nlp object
    for s in text:
        vector_sentence.append(nlp(s))

    graph = {}

    # Comparing each word in a sentence with every other word in the sentence
    for sentence in vector_sentence:
        for word1 in sentence:
            if not word1.has_vector:
                break

            for word2 in sentence:
                if not word2.has_vector or word2.text == word1.text:
                    break

                if word1.text not in graph:
                    graph[word1.text] = 0

                # Taking average and adding to dictionary
                graph[word1.text] = float((graph[word1.text] + word2.similarity(word1)) / 2)

    return graph

def get_key_words(vector_words_dict):
    """
    Given dictionary of each word and its similarity value, return the top 20 % of keywords
    """
    top_words = []
    for word, similarity in vector_words_dict.items():
        top_words.append((word, similarity))

    top_words = sorted(top_words, key=lambda x: x[1], reverse=True)

    num = round(len(top_words) * 0.2) # top 20 % words counter for
    if num < 1:
        num = 1
    return [top_words[x][0] for x in range(num)]

def keyword_count_in_sentences(keywords, sentences):
    """
    Given list of keywords, gives each sentence a score depending on the frequency of keyowrds in that sentence

    Returns:
         list : each index represents the count of a sentence at that index
    """
    count = [0] * len(sentences)

    for indx in range(len(sentences)):
        for word in sentences[indx].split():
            if word.lower() in keywords:
                count[indx] += 1
    return count

def run(long_text):
    """
    Given unedited text, the sentences are marked by importance

    Returns:
        (list, list) : (tokenized sentences, importance of each sentence)
    """
    tokenized_long_text = tokenization(long_text)
    final_long_text = remove_stop_words(tokenized_long_text)
    lemmatised_text = lemmatisation(final_long_text)
    vectorised_words_dict = vectorize_words(final_long_text)
    key_words = get_key_words(vectorised_words_dict)
    sentence_importance = keyword_count_in_sentences(key_words, lemmatised_text)
    return (tokenized_long_text, sentence_importance)

def summarize(text):
    return run(text)