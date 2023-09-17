import pandas as pd
import numpy as np
import ast
import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import bz2

# Loading datasets
credits = pd.read_csv("tmdb_5000_credits.csv")
movies = pd.read_csv("tmdb_5000_movies.csv")

# Merging movies and credits
movies = movies.merge(credits, on="title")
movies = movies[["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]]

# Drop missing values
movies.dropna(inplace=True)

# Convert genres and keywords from string to list
def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i["name"])
    return L

movies.genres = movies.genres.apply(convert)
movies.keywords = movies.keywords.apply(convert)

# Extracting top 3 casts
def convert3(obj):
    L = []
    counter = 0
    for i in ast.literal_eval(obj):
        if counter != 3:
            L.append(i["name"])
            counter += 1
        else:
            break
    return L

movies.cast = movies.cast.apply(convert3)

# Fetching director's name
def fetch_director(obj):
    L = []
    for i in ast.literal_eval(obj):
        if i["job"] == "Director":
            L.append(i["name"])
            break
    return L

movies.crew = movies.crew.apply(fetch_director)

# Preprocessing the data
movies.overview = movies.overview.apply(lambda x: x.split())
movies.genres = movies.genres.apply(lambda x: [i.replace(" ", "") for i in x])
movies.keywords = movies.keywords.apply(lambda x: [i.replace(" ", "") for i in x])
movies.cast = movies.cast.apply(lambda x: [i.replace(" ", "") for i in x])
movies.crew = movies.crew.apply(lambda x: [i.replace(" ", "") for i in x])

# Combining all the required columns to create tags
movies["tags"] = movies.overview + movies.genres + movies.keywords + movies.cast + movies.crew

# Creating a new DataFrame for movie recommendation
new_df = movies[["movie_id", "title", "tags"]]
new_df.tags = new_df.tags.apply(lambda x: " ".join(x))
new_df.tags = new_df.tags.apply(lambda x: x.lower())

# Stemming
ps = PorterStemmer()
new_df["tags"] = new_df["tags"].apply(lambda x: " ".join([ps.stem(i) for i in x.split()]))

# Creating a count vectorizer matrix
cv = CountVectorizer(max_features=5000, stop_words="english")
vectors = cv.fit_transform(new_df["tags"]).toarray()

# Calculating cosine similarity
similarity = cosine_similarity(vectors)

# Recommending movies
def recommend(movie):
    movie_index = new_df[new_df["title"] == movie].index[0]
    distance = similarity[movie_index]
    movies_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

    for i in movies_list:
        print(new_df.iloc[i[0]].title)

# Saving processed data for future use
pickle.dump(new_df.to_dict(), open("movie_dict.pkl", "wb"))
with bz2.BZ2File('similarity.pkl.bz2', 'wb') as f:
    pickle.dump(similarity, f)


