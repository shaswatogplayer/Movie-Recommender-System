import os
import pickle
import time
import streamlit as st
import gdown
import requests
import tempfile
import streamlit.components.v1 as components
import base64



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

def speak_movie_names(movie_list):
    api_key = st.secrets["ELEVEN_API_KEY"]

    text = "Here are the recommended movies for you. "

    for i, movie in enumerate(movie_list, start=1):
        text += f"Number {i}. {movie}. "

    url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"

    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        st.error(f"Voice generation failed ({response.status_code})")
        st.code(response.text)
        return None


    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        fp.write(response.content)
        return fp.name


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

    # ✅ Generate recommendations
    recommendations = recommend(selected_movie)

    # ✅ Display cards
    st.subheader("Recommended Movies")
    cols = st.columns(5)

    for idx, movie in enumerate(recommendations):
        time.sleep(0.15)
        with cols[idx]:
            st.markdown(
                f"<div class='movie-card'>{movie}</div>",
                unsafe_allow_html=True
            )

    # 🔊 Voice reads exactly the card content
    audio_file = speak_movie_names(recommendations)

    if audio_file:
        st.success("🔊 Playing voice recommendations")

        with open(audio_file, "rb") as audio:
            audio_bytes = audio.read()
            encoded_audio = base64.b64encode(audio_bytes).decode()

        components.html(
            f"""
            <audio autoplay hidden>
            <source src="data:audio/mpeg;base64,{encoded_audio}" type="audio/mpeg">
            </audio>
            """,
            height=0,
        )



