import json
import pickle

def clean_score(score):
    return {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
        '9': 9, '10': 10, 'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        '*': 1, '**': 2, '***': 3, '****': 4, '*****': 5, '******': 6,
        '*******': 7, '********': 8, '*********': 9, '**********': 10,
        'a': 4, 'b': 3, 'c': 2, 'd': 1, 'f': 0
    }.get(score.lower())

# reviews_pickle_path = 'pickles/reviews_df.pickle'
# with open(reviews_pickle_path, 'rb') as f:
    # reviews = pickle.load(f)

joined_reviews_path = 'data/joined_reviews.json'
with open(joined_reviews_path) as json_in:
    reviews = json.loads(json_in.read())

rs = [r['reviewer'] for r in reviews]

from collections import defaultdict

d = defaultdict(int)
for r in rs:
    d[r] += 1

import numpy as np

counts = np.array(sorted(d.values()))

counts

.8 * sum(counts)

sum(counts[counts > 15])

len(counts[counts > 15]) / len(counts)

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

five_star_regex = re.compile(r'([0-9]|one|two|three|four|five) stars', re.IGNORECASE)
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

# doc_lists = [
        # (leeper, 'leeper_reviews'),
        # (clean_n_star, 'clean_n_star_reviews'),
        # (unclean_n_star, 'unclean_n_star_reviews'),
        # (five_star, 'five_star_reviews'),
        # (letter_grade, 'letter_grade_reviews'),
        # (non_letter_grade, 'other_reviews'),
# ]

# for doc_list, name in doc_lists:
    # path = f"pickles/{name}.pickle"
    # with open(path, 'wb') as f:
        # pickle.dump(doc_list, f)

with open(f"pickles/leeper_reviews.pickle", 'rb') as f:
    leeper = pickle.load(f)
with open(f"pickles/clean_n_star_reviews.pickle", 'rb') as f:
    clean_n_star = pickle.load(f)
with open(f"pickles/unclean_n_star_reviews.pickle", 'rb') as f:
    unclean_n_star = pickle.load(f)
with open(f"pickles/five_star_reviews.pickle", 'rb') as f:
    five_star = pickle.load(f)
with open(f"pickles/letter_grade_reviews.pickle", 'rb') as f:
    letter_grade = pickle.load(f)
with open(f"pickles/other_reviews.pickle", 'rb') as f:
    non_letter_grade = pickle.load(f)

[review['document'][-100:] for review in non_letter_grade][:10]

scored = leeper + clean_n_star + five_star + letter_grade

# with open(f"pickles/scored_reviews.pickle", 'wb') as f:
    # pickle.dump(scored, f)

with open(f"pickles/scored_reviews.pickle", 'rb') as f:
    scored = pickle.load(f)

len(scored)

scored_movies = {review['title'] for review in scored}

# with open(f"pickles/scored_movies.pickle", 'wb') as f:
    # pickle.dump(scored_movies, f)

with open(f"pickles/scored_movies.pickle", 'rb') as f:
    scored_movies = pickle.load(f)

len(scored_movies)
