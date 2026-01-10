import os
import pickle
import time
import streamlit as st
import gdown

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Movie Recommender",
    layout="wide"
)

# ---------- DOWNLOAD PKL FILES ----------
SIMILARITY_FILE = "similarity.pkl"
MOVIES_FILE = "movie_list.pkl"

SIMILARITY_URL = "https://drive.google.com/uc?id=1H9QfkokFsBU0qSq9iATePxYPLEZ5kRmN"
MOVIES_URL = "https://drive.google.com/uc?id=1gfHfdZKUsXIfqM3ykvjXPrIwo_6rZR0C"

def download_if_not_exists():
    if not os.path.exists(SIMILARITY_FILE):
        gdown.download(SIMILARITY_URL, SIMILARITY_FILE, quiet=False)

    if not os.path.exists(MOVIES_FILE):
        gdown.download(MOVIES_URL, MOVIES_FILE, quiet=False)

download_if_not_exists()

# ---------- LOAD DATA ----------
movies = pickle.load(open(MOVIES_FILE, "rb"))
similarity = pickle.load(open(SIMILARITY_FILE, "rb"))

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #141e30, #243b55);
}

.main {
    background: linear-gradient(135deg, #141e30, #243b55);
}

.cover {
    background: linear-gradient(135deg, #cb2d3e, #ef473a);
    padding: 60px 30px;
    border-radius: 22px;
    margin-bottom: 40px;
    text-align: center;
    box-shadow: 0px 14px 35px rgba(0,0,0,0.45);
}

.cover-title {
    font-size: 52px;
    font-weight: 800;
    color: #ffffff;
}

.cover-subtitle {
    font-size: 18px;
    color: #ffe6e6;
    margin-top: 10px;
}

.movie-card {
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(12px);
    border-radius: 18px;
    padding: 25px;
    margin: 15px;
    text-align: center;
    font-size: 20px;
    font-weight: 600;
    color: red;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.35);
}

.movie-card:hover {
    transform: scale(1.06);
    box-shadow: 0px 14px 30px rgba(0,0,0,0.55);
}
</style>
""", unsafe_allow_html=True)

# ---------- LOGIC ----------
def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )
    return [movies.iloc[i[0]].title for i in distances[1:6]]

# ---------- COVER ----------
st.markdown("""
<div class="cover">
    <div class="cover-title">🎬 Movie Recommender System</div>
    <div class="cover-subtitle">
        Discover movies similar to what you love
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- UI ----------
selected_movie = st.selectbox(
    "Select a movie",
    movies["title"].values
)

if st.button("✨ Show Recommendation"):

    st.subheader("Generating recommendations...")

    progress = st.progress(0)
    status = st.empty()

    for i in range(0, 101, 5):
        time.sleep(0.05)
        progress.progress(i)
        status.text(f"Loading... {i}%")

    progress.empty()
    status.text("Completed")

    recommendations = recommend(selected_movie)

    st.subheader("Recommended Movies")
    cols = st.columns(5)

    for idx, movie in enumerate(recommendations):
        time.sleep(0.15)
        with cols[idx]:
            st.markdown(
                f"<div class='movie-card'>{movie}</div>",
                unsafe_allow_html=True
            )
