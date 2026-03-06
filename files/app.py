import streamlit as st
import moviever
import mood_engine
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

col1,col2,col3 = st.columns(3)
with col2:
    st.image(
        './Moviever_logo.jpg',
        width=200,
    )

st.title('The Movie Club', text_alignment= 'center')
st.subheader('Find your scene', text_alignment='center')
st.subheader('Let us know a bit about you:', text_alignment='left')


st.session_state.name = st.text_input(
    "What's your name?", 
    placeholder="Enter your name here",
)

st.session_state.movie1 = st.selectbox( 
    "Enter your favorite movie #1:", 
    options=['Avatar', 'The Matrix', 'Step Brothers', 'The Shining', 'The Great Gatsby']
)

st.session_state.movie2 = st.selectbox( 
    "Enter your favorite movie #2:", 
    options=["Pirates of the Caribbean: At World's End", 'Alien', 'The Hangover', 'Host', 'Hugo']
)

st.session_state.movie3 = st.selectbox( 
    "Enter your favorite movie #3:", 
    options=['Spectre', '2001: A Space Odyssey', 'Groundhog Day', 'The Conjuring', 'King Kong']
)

st.session_state.movie4 = st.selectbox( 
    "Enter your favorite movie #4:", 
    options=['The Dark Knight Rises', 'Blade Runner', 'Bridesmaids', 'The Exorcist', 'The Godfather']
)

st.session_state.movie5 = st.selectbox( 
    "Enter your favorite movie #5:",
    options=['John Carter', 'Tron: Legacy', 'Airplane!', 'Paranormal Activity', 'Titanic']
)

st.session_state.top5 = [
    st.session_state.movie1,
    st.session_state.movie2,
    st.session_state.movie3,
    st.session_state.movie4,
    st.session_state.movie5
]

if st.button('Join Movie Club! 🍿'):
    st.session_state.member = moviever.MovieverMember(name=st.session_state.name,
                        top5list=st.session_state.top5
    )

    st.session_state.club = st.session_state.member.vibe
    st.session_state.recommendations = mood_engine.get_tmdb_recommendations(st.session_state.member.vibe,
                                                                         api_key=API_KEY,
                                                                         excluded_film_ids=st.session_state.member.top_5_films)
    st.toast('Welcome to the Movie Club!',
             icon="🎬",
             duration='short')
    st.success(f"You're recommendations are {st.session_state.recommendations}") 