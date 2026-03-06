# The_Movie_Club

### Overview
Created a website that would place a user into a Movie Club based on their top 5 favourite films. The Clubs were linked to the films' sentiment, determined through genre and keyword analysis using the TMBD movie database API. Following placement in a movie club, users were recommended a film to watch as a Friday Movie Night, which fit the theme of their club, with 4 more films recommended as you might also like this. The **goal** of the project was to show that we could cluster movie watchers into groups based on their preferences and recommend them a matching film. The concept of the Friday Movie Night was to bring together movie-goers with similar interests and bring back the nostalgia of going to the movies.

### Technical description
The website was locally hosted on Streamlit as a proof-of-concept; the page was designed to have a welcome page that would collect the user's top 5 films and instantiate an object from the Movievermember class, from which club determination and movie recommendations would be completed. This class stores many instance variables, but most importantly, it stores the users' top 5 films, favourite genre, collected keywords, and club - the details of the class can be found in moviever.py.

The club (referred to as vibe in the code) was used to return the recommendations. The function get_tmdb_recommendations uses the vibe to tailor an API call based on that vibe to the TMDB database, returning a list of matching movies from which a random sample of 5 movies is returned. This function can be found in mood_engine.py.
