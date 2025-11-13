import streamlit as st
import pickle
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ----------------------------------------------------------
# Load your new PKL files
# ----------------------------------------------------------
movies = pickle.load(open("movie_list (1).pkl", "rb"))
similarity = pickle.load(open("similarity (1).pkl", "rb"))

API_KEY = "3d68cc4837e0d5e379e1e719c8214058"

# requests session with retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))


# ----------------------------------------------------------
# Fetch Poster (safe version)
# ----------------------------------------------------------
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        resp = session.get(url, timeout=6)

        if resp.status_code != 200:
            return "https://via.placeholder.com/500x750?text=No+Image"

        data = resp.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path

    except Exception as e:
        print("Poster error:", e)

    return "https://via.placeholder.com/500x750?text=No+Image"


# ----------------------------------------------------------
# Recommend movies for NEW similarity.pkl structure
# (top-20 indices stored, not full cosine matrix)
# ----------------------------------------------------------
def recommend(movie):
    index = movies[movies["title"] == movie].index[0]

    # the similarity file contains only indexes, not cosine values
    similar_indices = similarity[index]     # list of 20 indexes

    names = []
    posters = []

    for i in similar_indices[:6]:  # top 6
        movie_id = movies.iloc[i].movie_id
        names.append(movies.iloc[i].title)
        posters.append(fetch_poster(movie_id))

    return names, posters


# ----------------------------------------------------------
# Streamlit UI
# ----------------------------------------------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

st.markdown(
    """
    <h1 style="text-align:center; color:#FF4B4B;">🎬 Movie Recommendation System</h1>
    <p style="text-align:center; font-size:18px;">Find similar movies instantly</p>
    """,
    unsafe_allow_html=True
)

selected_movie = st.selectbox("Select a movie:", movies["title"].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    cols = st.columns(3)
    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx], use_container_width=True)
            st.write(f"**{names[idx]}**")

    cols2 = st.columns(3)
    for idx, col in enumerate(cols2):
        with col:
            st.image(posters[idx+3], use_container_width=True)
            st.write(f"**{names[idx+3]}**")
