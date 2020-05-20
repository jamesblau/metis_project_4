import os
import json
import numpy as np
import pandas as pd
import pickle

with open('data/reviews.json') as json_in:
    reviews = json.loads(json_in.read())
# reviews = reviews[:1000]
documents = []
for review in reviews:
    document = ""
    for paragraph in review['paragraphs']:
        if paragraph[:10] != "Synopsis: ":
            document += paragraph + " "
    documents += [document]
df = pd.DataFrame(joined, columns=['data'])

################################################################################

# import corextopic
# import networkx

# import scipy.sparse as ss

# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn import datasets

# from corextopic import corextopic as ct
# from corextopic import vis_topic as vt

# import matplotlib.pyplot as plt
# import seaborn as sns

################################################################################

# import spacy
# nlp = spacy.load('en_core_web_sm')

# doc = nlp(joined[0])

# for token in doc:
    # print(token.text, token.pos_, token.lemma_, token.is_stop)

################################################################################

import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en.stop_words import STOP_WORDS
# import en_core_web_lg

from tqdm import tqdm
from pprint import pprint

import spacy
nlp = spacy.load('en_core_web_sm')

# My list of stop words.
# stop_list = [
    # "car", "character", "day", "effect", "end", "film", "find", "good",
    # "know", "life", "like", "movie", "play", "story", "thing", "think",
    # "time", "way", "work",
# ]

# Updates spaCy's default stop words list with my additional words.
# nlp.Defaults.stop_words.update(stop_list)

# Iterates over the words in the stop words list and resets the "is_stop" flag.
# for word in STOP_WORDS:
    # lexeme = nlp.vocab[word]
    # lexeme.is_stop = True

def lemmatizer(doc):
    # This takes in a doc of tokens from the NER and lemmatizes them.
    # Pronouns (like "I" and "you" get lemmatized to '-PRON-', so I'm removing those.
    doc = [token.lemma_ for token in doc if token.lemma_ != '-PRON-']
    doc = u' '.join(doc)
    return nlp.make_doc(doc)

def remove_stopwords(doc):
    # This will remove stopwords and punctuation.
    # Use token.text to return strings, which we'll need for Gensim.
    doc = [token.text for token in doc if token.is_stop != True and token.is_punct != True]
    return doc

# The add_pipe function appends our functions to the default pipeline.
nlp.add_pipe(lemmatizer,name='lemmatizer',after='ner')
nlp.add_pipe(remove_stopwords, name="stopwords", last=True)

doc_list = []
# Iterates through each article in the corpus.
for doc in tqdm(df['data']):
    # Passes that article through the pipeline and adds to a new list.
    pr = nlp(doc)
    doc_list.append(pr)

# with open('pickles/review_doc_list_1.pickle', 'wb') as f:
    # pickle.dump(doc_list, f)

with open('pickles/review_doc_list_1.pickle', 'rb') as f:
    doc_list = pickle.load(f)

# Creates, which is a mapping of word IDs to words.
words = corpora.Dictionary(doc_list)

# Turns each document into a bag of words.
corpus = [words.doc2bow(doc) for doc in doc_list]

lda = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                           id2word=words,
                                           num_topics=10,
                                           random_state=2,
                                           update_every=1,
                                           passes=10,
                                           alpha='auto',
                                           per_word_topics=True)

# with open('pickles/review_lda_1.pickle', 'wb') as f:
    # pickle.dump(lda, f)

with open('pickles/review_lda_1.pickle', 'rb') as f:
    lda = pickle.load(f)

pprint(lda.print_topics(num_words=10))

################################################################################

from wordcloud import WordCloud, STOPWORDS

for t in range(lda.num_topics):
    plt.figure()
    plt.imshow(WordCloud().fit_words(dict(lda.show_topic(t, 200))))
    plt.axis("off")
    plt.title("Topic #" + str(t))
    plt.show()
