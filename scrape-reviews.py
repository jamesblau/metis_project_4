import os
import json
import pickle
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from pymongo import MongoClient

client = MongoClient()

# Load titles for which I have both scripts and reviews

common_compressed = \
    list(client.movies.common_titles_compressed.find())[0]['titles']

# Load mapping between full and compressed titles

mapping_dicts = list(client.movies.titles_mapping.find())
jmap_common = [j for j in mapping_dicts
        if j['compressed'] in common_compressed]
full_to_compressed = {j['full']: j['compressed'] for j in jmap_common}
common_titles = [j['full'] for j in jmap_common]

# Parse review html

title_regex = re.compile(r'^([^(]*).*$')

reviews_dir = '/home/james/movies/polarity/movie/'

reviews_path = 'data/reviews.json'

with open(reviews_path, 'a') as json_out:
    json_out.write('[\n')
    filenames = os.listdir(reviews_dir)
    num_files = len(filenames)
    read = 0
    counted = 0
    for index, filename in enumerate(filenames):
        read += 1
        with open(reviews_dir + filename, encoding="ISO-8859-1") as review_in:
            html = review_in.read()
        if html:
            soup = BeautifulSoup(html, 'lxml')
            attrs = []
            for attr in soup.find_all('a'):
                if attr.contents:
                    attrs.append(str(attr.contents[0]))
            title = title_regex.search(attrs[0]).group(1).strip()
            compressed = full_to_compressed.get(title)
            if compressed:
                counted += 1
                reviewer = attrs[1]
                paragraphs = []
                first_pre = soup.find('pre')
                if first_pre:
                    for tag in first_pre.next_siblings:
                        if tag.name == "pre":
                            break
                        else:
                            for paragraph in tag:
                                if type(paragraph) is NavigableString:
                                    paragraphs.append(str(paragraph.replace('\n', ' ')))
                    paragraphs = [p for p in paragraphs if len(p) > 50]
                if paragraphs == []:
                    for p in soup.find_all('p'):
                        if p.find_all() == []:
                            contents = p.contents
                            if contents:
                                paragraphs.append(contents[0].replace('\n', ' '))
                pres = []
                for pre in soup.find_all('pre'):
                    if pre.contents:
                        pres.append(str(pre.contents[0]))
                j = json.dumps({
                    'id': filename,
                    'reviewer': reviewer,
                    'compressed': compressed,
                    'title': title,
                    'paragraphs': paragraphs,
                    'pres': pres,
                    'attrs': attrs[2:],
                })
                json_out.write(j)
                if index != num_files - 1:
                    json_out.write(',')
                json_out.write('\n')
    json_out.write(']')

# I didn't want to run that again when making some additions
# So reload reviews

with open(reviews_path) as json_in:
    reviews = json.loads(json_in.read())

# Write final parsed reviews to mongo

collection = client.movies.reviews
for review in reviews:
    document = ""
    for paragraph in review['paragraphs']:
        if paragraph[:10] != "Synopsis: ":
            document += paragraph + " "
    document = re.sub('\s+', ' ', document.strip())
    review['document'] = document
    del review['paragraphs']
    review['id'] = review['id'].split('.')[0]
    collection.insert_one(review)
