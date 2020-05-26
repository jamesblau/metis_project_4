import pandas as pd
import pickle
from collections import defaultdict

from pymongo import MongoClient

import gensim.corpora as corpora
from gensim.models.ldamodel import LdaModel

import spacy
from spacy.lang.en.stop_words import STOP_WORDS

import nltk
from nltk.corpus import stopwords, names

from tqdm import tqdm
from pprint import pprint

from wordcloud import WordCloud, STOPWORDS

# Only had to run once
# nltk.download('stopwords')
# nltk.download('names')

# Pandas options
pd.set_option('max_columns', None)
pd.set_option('max_rows', 20)

# Load parsed reviews
client = MongoClient()
reviews = pd.DataFrame(list(client.movies.reviews.find()))

# Get stopwords from previous attempts at topic modelling (see below)
with open('pickles/common_words.pickle', 'rb') as f:
    common_words = pickle.load(f)

# Combine stop words from three sources
sw = {word.lower() for word in stopwords.words('english') + names.words()}
sw = sw | STOP_WORDS | common_words

# Start up nlp pipeline
nlp = spacy.load('en_core_web_sm')

# Load stop words
nlp.Defaults.stop_words.update(sw)
for word in sw:
    lexeme = nlp.vocab[word]
    lexeme.is_stop = True

def remove_stopwords(doc):
    doc = [token.text for token in doc
            if token.is_stop != True and token.is_punct != True]
    return doc

# Lemmatizing helped
def lemmatizer(doc):
    doc = [token.lemma_ for token in doc if token.lemma_ != '-PRON-']
    doc = u' '.join(doc)
    return nlp.make_doc(doc)

# Create and apply pipeline to lemmatize and remove stop words

nlp.add_pipe(lemmatizer,name='lemmatizer',after='ner')
nlp.add_pipe(remove_stopwords, name="stopwords", last=True)

doc_list = []
for doc in tqdm(reviews['doc']):
    pr = nlp(doc.lower())
    doc_list.append(pr)

# That was slow, so pickle

# with open('pickles/review_doc_list_3.pickle', 'wb') as f:
    # pickle.dump(doc_list, f)

with open('pickles/review_doc_list_3.pickle', 'rb') as f:
    doc_list = pickle.load(f)

# Create word mapping and bags of words
words = corpora.Dictionary(doc_list)
corpus = [words.doc2bow(doc) for doc in doc_list]

# Create LDA model
lda = LdaModel(corpus=corpus,
               id2word=words,
               num_topics=10,
               random_state=2,
               update_every=1,
               passes=10,
               alpha='auto',
               per_word_topics=True)

# Pickle that too

# with open('pickles/review_lda_2.pickle', 'wb') as f:
    # pickle.dump(lda, f)

with open('pickles/review_lda_2.pickle', 'rb') as f:
    lda = pickle.load(f)

# Let's look at the results

pprint(lda.print_topics(num_words=10))

# Some words seem too generic to movies and common across topics
# Let's add them to stop words, pickle them, comment this out, and rerun

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

# Generate wordclouds
for t in range(lda.num_topics):
    wc = WordCloud(width=800, height=400)
    wc.fit_words(dict(lda.show_topic(t, 200)))
    plt.figure()
    plt.imshow(wc)
    plt.axis("off")
    plt.show()
