import json
import numpy as np
import pandas as pd
import pickle
from collections import defaultdict

import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel

import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en.stop_words import STOP_WORDS
# import en_core_web_lg

import nltk
from nltk.corpus import stopwords, names

from tqdm import tqdm
from pprint import pprint

# nltk.download('stopwords')
# nltk.download('names')

pd.set_option('max_columns', None)
pd.set_option('max_rows', 20)

reviews_pickle_path = 'pickles/reviews_df.pickle'
with open(reviews_pickle_path, 'rb') as f:
    reviews = pickle.load(f)

# From previous attempts
with open('pickles/common_words.pickle', 'rb') as f:
    common_words = pickle.load(f)

sw = {word.lower() for word in stopwords.words('english') + names.words()}
sw = sw | STOP_WORDS | common_words

nlp = spacy.load('en_core_web_sm')

nlp.Defaults.stop_words.update(sw)

# Iterates over the words in the stop words list and resets the "is_stop" flag.
for word in sw:
    lexeme = nlp.vocab[word]
    lexeme.is_stop = True

def lemmatizer(doc):
    # This takes in a doc of tokens from the NER and lemmatizes them.
    # Pronouns (like "I" and "you" get lemmatized to '-PRON-', so I'm removing those.
    doc = [token.lemma_ for token in doc if token.lemma_ != '-PRON-']
    doc = u' '.join(doc)
    return nlp.make_doc(doc)

def remove_stopwords(doc):
    # This will remove stopwords and punctuation.
    # Use token.text to return strings, which we'll need for Gensim.
    doc = [token.text for token in doc
            if token.is_stop != True and token.is_punct != True]
    return doc

nlp.add_pipe(lemmatizer,name='lemmatizer',after='ner')
nlp.add_pipe(remove_stopwords, name="stopwords", last=True)

doc_list = []
# for doc in tqdm(reviews['doc'].head(100)):
for doc in tqdm(reviews['doc']):
    pr = nlp(doc.lower())
    doc_list.append(pr)

# with open('pickles/review_doc_list_2.pickle', 'wb') as f:
    # pickle.dump(doc_list, f)

with open('pickles/review_doc_list_2.pickle', 'rb') as f:
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

# with open('pickles/review_lda_2.pickle', 'wb') as f:
    # pickle.dump(lda, f)

with open('pickles/review_lda_2.pickle', 'rb') as f:
    lda = pickle.load(f)

pprint(lda.print_topics(num_words=10))

# top_words = lda.print_topics(num_words=40)
# counts = defaultdict(int)
# for topic in top_words:
    # score_words = topic[1].split(" + ")
    # for score_word in score_words:
        # word = score_word.split('"')[1]
        # counts[word] += 1
# common_words = {word for word, count in counts.items() if count > 2}

# with open('pickles/common_words.pickle', 'wb') as f:
    # pickle.dump(common_words, f)

################################################################################

from wordcloud import WordCloud, STOPWORDS

for t in range(lda.num_topics):
    wc = WordCloud(width=800, height=400)
    wc.fit_words(dict(lda.show_topic(t, 200)))
    plt.figure()
    plt.imshow(wc)
    plt.axis("off")
    plt.show()
