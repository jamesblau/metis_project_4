from collections import defaultdict
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.linalg import svd

from pymongo import MongoClient

# I ended up with a simple collaborative recommender

# Load scored reviews
client = MongoClient()
df = pd.DataFrame(list(client.movies.scored_reviews.find()))
df = df.rename(columns={'reviewer': 'user'})[['user', 'title', 'score']]

# Change score domain from [-1, 1] to [0,1]
df['score'] = df['score'].apply(lambda score: (score + 1) / 2)

# Convert users and movies to numeric ids: uids and mids

uid_2_user = dict(enumerate(set(df['user'])))
user_2_uid = {user: uid for uid, user in uid_2_user.items()}

mid_2_title = dict(enumerate(set(df['title'])))
title_2_mid = {title: mid for mid, title in mid_2_title.items()}
title_2_mid

df['uid'] = df['user'].apply(lambda user: user_2_uid[user])
df['mid'] = df['title'].apply(lambda user: title_2_mid[user])

# Set up SVD
user_item_matrix = coo_matrix((df['score'], (df['uid'], df['mid']))).toarray()
U, S, V = svd(user_item_matrix)

# Pull recommendations; code adapted from pair with Fong Wa

def rec_similar(mids, num_recs=3):
    recs = defaultdict(float)
    for mid in mids:
        for candidate in range(V.T.shape[0]):
            if candidate != mid:
                recs[candidate] += np.dot(V.T[mid], V.T[candidate])
    sorted_recs = sorted(recs.items(), key=lambda x: x[1], reverse=True)
    sorted_movies = [i[0] for i in sorted_recs]
    return sorted_movies[:num_recs]

def print_similar_titles(titles_in, num_recs=3):
    mids_in = [title_2_mid[title] for title in titles_in]
    mids_out = rec_similar(mids_in, num_recs)
    titles_out = [mid_2_title[mid] for mid in mids_out]
    print(f"For {titles_in}, I recommend:")
    for title in titles_out:
        print(title)

def user_recs(uid, num_recs=3):
    similar_users = []
    for other_user in range(U.shape[0]):
        if other_user != uid:
            similar_users.append([other_user, np.dot(U[uid], U[other_user])])
    similar_users = [i[0] for i in
            sorted(similar_users, key=lambda x: x[1], reverse=True)]
    closest_user_scores = user_item_matrix[similar_users[0]]
    recs = []
    for i, mid in enumerate(user_item_matrix[uid]):
        if mid != closest_user_scores[i] and closest_user_scores[i]!=0:
            recs.append(i)
    return recs[:num_recs]

# Some of these look pretty reasonable
print_similar_titles(titles_in=[
        'Alien',
        'Alien: Resurrection',
        'Blade Runner',
    ],
    num_recs=2
)
# For ['Alien', 'Alien: Resurrection', 'Blade Runner'], I recommend:
# Star Trek: First Contact
# Gattaca
