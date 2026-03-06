import streamlit as st
import pandas as pd
from Posterpath import get_poster_path, get_movie, other_movies, vibe_poster
import datetime
from random import randint

col1,col2,col3 = st.columns(3)
with col2:
    st.image(
        './Moviever_logo.jpg',
        width=200,
    )

st.title(f'Hey {st.session_state.name},', 
         text_alignment='center')

x = datetime.datetime.now()
st.write(f'**Date:** {x.strftime("%A, %b %d, %Y")}')

col1, col2 = st.columns(2,gap='large', border=True)

st.session_state.movie = st.session_state.recommendations[randint(0, len(st.session_state.recommendations)-1)]

with col1:
    st.subheader('Your Club:',
                 text_alignment='left')
    st.subheader(st.session_state.club,
                 text_alignment='left'
    )
    try:
        st.image(
            vibe_poster(st.session_state.club),
            use_container_width=True
        )
    except:
        st.write("*Poster not available*")
        st.write(st.session_state.club)

with col2:
    st.subheader('Friday Movie Night🍿',
                  text_alignment='left')
    try:
        st.image(
        get_poster_path(st.session_state.movie), 
        caption=st.session_state.movie,
        use_container_width=True
    )
    except:
        st.write("*Poster not available*")
        st.write(st.session_state.movie)

similar_movies, release_year = other_movies(st.session_state.recommendations,
                                             st.session_state.movie, 
                                             count=5)

st.session_state.data = {
    'Title': similar_movies,
    'Release Year': release_year
}

df = pd.DataFrame(st.session_state.data)

st.subheader('You might also like:', text_alignment='left')
st.table(df)
