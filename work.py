import os
import json
import numpy as np
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString

common_titles_file = 'common_titles_compressed'
with open(common_titles_file) as f:
    common = f.read().strip().split('\n')

len(common)

mapping_file = 'titles_mapping_ISO-8859'
with open(mapping_file, encoding="ISO-8859-1") as f:
    mapping = f.read().strip().split('\n')

len(mapping)

mapping[-1]

jmap = [json.loads(m) for m in mapping]

jmap[-1]

jmap_common = [j for j in jmap if j['compressed'] in common]

common_titles = [j['full'] for j in jmap_common]

len(common_titles)

# with open('/home/james/film_aggs/common_titles_mapping', 'a') as f:
    # for j in jmap_common:
        # f.write(str(j) + '\n')


title_regex = re.compile(r'^Review for ([^(]*).*$')

reviews_dir = '/home/james/movies/polarity/movie/'

for name in os.listdir(reviews_dir)[:100]:
    with open(reviews_dir + name, encoding="ISO-8859-1") as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')
    html_title = soup.find(name='title').contents[0]
    title = title_regex.search(html_title).group(1).strip()
    # compressed = 
    if title in common_titles:
        paragraphs = []
        for tag in soup.find('pre').next_siblings:
            if tag.name == "pre":
                break
            else:
                for paragraph in tag:
                    if type(paragraph) is NavigableString:
                        paragraphs.append(str(paragraph.replace('\n', ' ')))
        pres = [pre.contents for pre in soup.find_all('pre')]

pres
