import requests
from random import sample
from config import read

read_access = read

def get_poster_path(title):
    url = f'https://api.themoviedb.org/3/search/movie'
    
    headers = {
    "Authorization": f"Bearer {read_access}",
    "Accept": "application/json"
}
    
    params = {
    'query' : title,
    'page' : 1
}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if data['results']:
        poster_path = data['results'][0]['poster_path']
        full_poster_url = f'https://image.tmdb.org/t/p/w500{poster_path}'
        return full_poster_url
    else:
        return None

def get_movies(genre):
    TMDB_MOVIE_GENRES = {
    "Action": 28,
    "Adventure": 12,
    "Animation": 16,
    "Comedy": 35,
    "Crime": 80,
    "Documentary": 99,
    "Drama": 18,
    "Family": 10751,
    "Fantasy": 14,
    "History": 36,
    "Horror": 27,
    "Music": 10402,
    "Mystery": 9648,
    "Romance": 10749,
    "Science Fiction": 878,
    "TV Movie": 10770,
    "Thriller": 53,
    "War": 10752,
    "Western": 37
}
    genre_id = TMDB_MOVIE_GENRES[genre]
    if not genre_id:
        return None
    
    url = 'https://api.themoviedb.org/3/discover/movie'
    headers = {
        "Authorization": f"Bearer {read_access}",
    "Accept": "application/json"
}
    params = {
    "with_genres": genre_id,
    "sort_by": "vote_average.desc",
    "vote_count.gte": 1000,
    "page": 1,
    "include_adult": "false"
}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if data['results']:
        return data['results']
    else:
        return None

def get_movie(title):
    url = 'https://api.themoviedb.org/3/search/movie'
    headers = {
        "Authorization": f"Bearer {read_access}",
    "Accept": "application/json"
}
    params = {
        "query": title,
        "page": 1
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if data['results']:
        return data['results'][0]
    else:
        return None


def other_movies(movies, title, count=4):
    selected_movies = []
    release_dates = []

    for movie in sample(movies, count):
        data = get_movie(movie)
        if data and data['title'] != title:
            selected_movies.append(data['title'])
            release_dates.append(data['release_date'][:4])

    return selected_movies, release_dates

def vibe_poster(vibe):
    vibe = vibe.replace(' ', '_')
    return f'./club_posters/{vibe}.png'