import os
import json
import pickle
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString

common_titles_file = 'common_titles_compressed'
with open(common_titles_file) as titles_in:
    common = titles_in.read().strip().split('\n')

len(common)

mapping_file = 'titles_mapping_ISO-8859'
with open(mapping_file, encoding="ISO-8859-1") as mapping_in:
    mapping = mapping_in.read().strip().split('\n')

len(mapping)

mapping[-1]

jmap = [json.loads(m) for m in mapping]

jmap[-1]

jmap_common = [j for j in jmap if j['compressed'] in common]

full_to_compressed = {j['full']: j['compressed'] for j in jmap_common}

common_titles = [j['full'] for j in jmap_common]

len(common_titles)

with open('data/common_titles_mapping.json', 'a') as mapping_out:
    mapping_out.write('[\n')
    for index, jsn in enumerate(jmap_common):
        mapping_out.write(json.dumps(jsn))
        if index != len(jmap_common) - 1:
            mapping_out.write(',')
        mapping_out.write('\n')
    mapping_out.write(']')


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

with open(reviews_path) as json_in:
    reviews = json.loads(json_in.read())

joined_reviews_path = 'data/joined_reviews.json'

with open(joined_reviews_path, 'a') as json_out:
    json_out.write('[\n')
    num_files = len(reviews)
    documents = []
    for index, review in enumerate(reviews):
        document = ""
        for paragraph in review['paragraphs']:
            if paragraph[:10] != "Synopsis: ":
                document += paragraph + " "
        document = re.sub('\s+', ' ', document.strip())
        documents += [document]
        review['document'] = document
        del review['paragraphs']
        review['id'] = review['id'].split('.')[0]
        json_out.write(json.dumps(review))
        if index != num_files - 1:
            json_out.write(',')
        json_out.write('\n')
    json_out.write(']')

review_rows = []
for r in reviews:
    review_rows.append([r['id'], r['reviewer'], r['title'], r['document']])

columns = ['id', 'reviewer', 'title', 'doc']
df = pd.DataFrame(review_rows, columns=columns)

reviews_pickle_path = 'pickles/reviews_df.pickle'
with open(reviews_pickle_path, 'wb') as f:
    pickle.dump(df, f)
