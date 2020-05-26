from collections import defaultdict
import json
import pickle
import numpy as np

from pymongo import MongoClient

def clean_score(score):
    return {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
        '9': 9, '10': 10, 'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        '*': 1, '**': 2, '***': 3, '****': 4, '*****': 5, '******': 6,
        '*******': 7, '********': 8, '*********': 9, '**********': 10,
        'a': 4, 'b': 3, 'c': 2, 'd': 1, 'f': 0
    }.get(score.lower())

# Load parsed reviews
client = MongoClient()
reviews = list(client.movies.reviews.find())

# Get some stats on reviewers

rs = [r['reviewer'] for r in reviews]

d = defaultdict(int)
for r in rs:
    d[r] += 1

counts = np.array(sorted(d.values()))

sum(counts[counts >= 10]) / sum(counts)
# ~80% reviewers wrote at least ten

len(counts[counts >= 10]) / len(counts)
# That's about 14% of reviewers

# Let's see how many scores we can easily parse

# Several people use this Leeper guy's -4.0 to 4.0 system
leeper_regex = re.compile(r'([-+]?\d+)[^.]*-4[^.]*\+?4')
leeper = []
non_leeper = []
for review in reviews:
    search = leeper_regex.search(review['document'])
    if search:
        review['score'] = int(search.group(1)) / 4
        leeper.append(review)
    else:
        non_leeper.append(review)
len(leeper), len(non_leeper)

# Some people specify how many stars they review out of
n_star_regex = re.compile(r'([^a-zA-Z ]*) stars[^.]*out of ([^ .]*)')
n_star = []
non_n_star = []
for review in non_leeper:
    search = n_star_regex.search(review['document'])
    if search:
        n_star.append((review, search.group(1), search.group(2)))
    else:
        non_n_star.append(review)
len(n_star), len(non_n_star)

# Some of those I can easily parse
clean_n_star = []
unclean_n_star = []
for review, score, out_of in n_star:
    cleaned_score = clean_score(score)
    cleaned_out_of = clean_score(out_of)
    if cleaned_score and cleaned_out_of:
        review['score'] = 2 * (cleaned_score / cleaned_out_of) - 1
        clean_n_star.append(review)
    else:
        unclean_n_star.append((review, score, out_of))
len(clean_n_star), len(unclean_n_star)

# Assume anyone who doesn't specify max stars is rating out of five stars
five_star_regex = \
    re.compile(r'([0-9]|one|two|three|four|five) stars', re.IGNORECASE)
five_star = []
non_five_star = []
for review in non_n_star:
    search = five_star_regex.search(review['document'])
    if search:
        review['score'] = clean_score(search.group(1)) * (2 / 5) - 1
        five_star.append(review)
    else:
        non_five_star.append(review)
len(five_star), len(non_five_star)

# I can easily parse letter grades that have + or -
letter_grade_regex = re.compile(r'[^a-zA-Z0-9]([A-F])[-+][^a-zA-Z0-9]')
letter_grade = []
non_letter_grade = []
for review in non_five_star:
    search = letter_grade_regex.search(review['document'])
    if search:
        review['score'] = (clean_score(search.group(1)) / 2) - 1
        letter_grade.append(review)
    else:
        non_letter_grade.append(review)
len(letter_grade), len(non_letter_grade)

# Combine all reviews with parsed scores

scored = leeper + clean_n_star + five_star + letter_grade

# Write to mongo

collection = client.movies.scored_reviews
for review in scored:
    collection.insert_one(review)

len(scored)
# 542 reviews with parsed scores

scored_movies = {review['title'] for review in scored}

len(scored_movies)
# 274 scored movies
