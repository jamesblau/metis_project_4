import os
import pandas as pd
import pickle

from pymongo import MongoClient

import gensim.corpora as corpora
from gensim.models.ldamodel import LdaModel

import spacy
from spacy.lang.en.stop_words import STOP_WORDS

import nltk
from nltk.corpus import stopwords, names

from tqdm import tqdm
from pprint import pprint

from review-topics import remove_stopwords, lemmatizer

from wordcloud import WordCloud, STOPWORDS

# I played around with this, didn't get good results

# Pandas options
pd.set_option('max_columns', None)
pd.set_option('max_rows', 20)

# I played around with cleaning the text in different ways
def clean_text(text):
    text = text.lower()
    text = re.sub('\s+', ' ', text)
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('\xa0', '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = text.strip()
    return text

# Load scripts

client = MongoClient()
scripts_json = list(client.movies.scripts.find())
df = pd.DataFrame(scripts_json)

# Combine stop words from two sources
sw = {word.lower() for word in stopwords.words('english') + names.words()}
sw = sw | STOP_WORDS

# Start up nlp pipeline
nlp = spacy.load('en_core_web_sm')

# Load stop words
nlp.Defaults.stop_words.update(sw)
for word in sw:
    lexeme = nlp.vocab[word]
    lexeme.is_stop = True

# Create and apply pipeline to lemmatize and remove stop words

nlp.add_pipe(lemmatizer,name='lemmatizer',after='ner')
nlp.add_pipe(remove_stopwords, name="stopwords", last=True)

doc_list = []
for doc in tqdm(reviews['doc']):
    pr = nlp(doc.lower())
    doc_list.append(pr)

# That was *really* slow, so pickle

# with open('pickles/movie_doc_list_4.pickle', 'wb') as f:
    # pickle.dump(doc_list, f)

with open('pickles/movie_doc_list_4.pickle', 'rb') as f:
    doc_list = pickle.load(f)

# Create word mapping and bags of words
words = corpora.Dictionary(doc_list)
corpus = [words.doc2bow(doc) for doc in doc_list]

# Create LDA model
lda = LdaModel(corpus=corpus,
               id2word=words,
               num_topics=3,
               random_state=2,
               update_every=1,
               passes=20,
               alpha='auto',
               per_word_topics=True)

# Pickle that too

# with open('pickles/movie_lda_1.pickle', 'wb') as f:
    # pickle.dump(lda, f)

with open('pickles/movie_lda_1.pickle', 'rb') as f:
    lda = pickle.load(f)

pprint(lda.print_topics(num_words=10))

# Generate wordclouds
for t in range(lda.num_topics):
    wc = WordCloud(width=800, height=400)
    wc.fit_words(dict(lda.show_topic(t, 200)))
    plt.figure()
    plt.imshow(wc)
    plt.axis("off")
    plt.show()
