from moviever import MovieverMember
import streamlit as st

col1,col2,col3 = st.columns(3)
with col2:
    st.image(
        './Moviever_logo.jpg',
        width=200,
    )

st.title('Rewards Hub 🎁', text_alignment='center')

col1, col2 = st.columns(2, border=True)
with col1:
    st.subheader('Your Points', text_alignment='left')
    st.header(f"{st.session_state.member.points} Points", text_alignment='center')

with col2:
    st.subheader('Your Rank', text_alignment='left')
    st.header(st.session_state.member.rank, text_alignment='center')

st.progress((st.session_state.member.points % 200) / 200, text=f"{200 - (st.session_state.member.points % 200)} points to next level!",)