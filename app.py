import streamlit as st
import pandas as pd
import pickle
import bz2
import requests

def fetch_poster(movie_id):
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=e81dd9737aac1632c92c3216713e7831&language=en-US")
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]

def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distance = similarity[movie_index]
    movies_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_poster = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_poster.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_poster

st.markdown(
    """
    <style>
        :root {
            --primary-bg: #1F1F1F;
            --secondary-bg: #2A2A2A;
            --primary-text: #E8E8E8;
            --secondary-text: #B0B0B0;
            --highlight: #FF176B;
        }

        body {
            background-color: var(--primary-bg);
        }

        .stApp {
            color: var(--primary-text);
        }

        .stButton>button {
            background-color: var(--highlight) !important;
            border: none !important;
            border-radius: 5px !important;
            transition: background-color 0.2s !important;
        }

        .stButton>button:hover {
            background-color: var(--primary-text) !important;
        }

        .stButton>button:focus {
            background-color: var(--highlight) !important;
            box-shadow: 0 0 0 2px var(--primary-bg), 0 0 0 4px var(--highlight) !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Movie Recommendation System")

movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

with bz2.BZ2File('similarity.pkl.bz2', 'rb') as f:
    similarity = pickle.load(f)

selected_movie_name = st.selectbox("Enter your movie", movies["title"].values)

if st.button("Recommend Movie"):
    names, posters = recommend(selected_movie_name)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(names[0])
        st.image(posters[0], use_column_width=True)
    with col2:
        st.text(names[1])
        st.image(posters[1], use_column_width=True)
    with col3:
        st.text(names[2])
        st.image(posters[2], use_column_width=True)
    with col4:
        st.text(names[3])
        st.image(posters[3], use_column_width=True)
    with col5:
        st.text(names[4])
        st.image(posters[4], use_column_width=True)
