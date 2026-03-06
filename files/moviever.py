import time
import requests
import os
from dotenv import load_dotenv
from random import randint
from film_deserialisation import SearchResponse, MovieDetail
from mood_engine import calculate_dominant_vibe, match_vibe_input, get_tmdb_recommendations

load_dotenv()
API_KEY = os.getenv("API_KEY")

# Matches with existing database...
GENRE_ID_MAP = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
    80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
    14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
    9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
}

def search_film(film_name, api_key=API_KEY):
    """
    Finds a film on TMDB using its name.
    """
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": api_key,
        "query": film_name,
        "include_adult": "false"
        }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return SearchResponse(**response.json())
    except Exception as e:
        print(f"Error searching: {e}")
        return None

def get_movie_details(movie_id, api_key=API_KEY):
    """
    Gets the director and keywords for a specific movie.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    
    params = {
        "api_key": api_key,
        "append_to_response": "credits,keywords" 
    }
    
    director = "Unknown Director"
    keywords_list = []

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        details = MovieDetail(**response.json())
        
        # 1. Find Director
        for crew in details.credits.crew:
            if crew.job == "Director":
                director = crew.name
                break
        
        # 2. Extract Keywords
        keywords_list = [k.name for k in details.keywords.keywords]
        
        return director, keywords_list
        
    except Exception:
        return director, keywords_list


class MovieverMember:
    ALL_GENRES = {
        "Action": 0, "Adventure": 0, "Animation": 0, "Comedy": 0, 
        "Crime": 0, "Documentary": 0, "Drama": 0, "Family": 0, 
        "Fantasy": 0, "History": 0, "Horror": 0, "Music": 0, 
        "Mystery": 0, "Romance": 0, "Science Fiction": 0, 
        "TV Movie": 0, "Thriller": 0, "War": 0, "Western": 0
    }

    ranks = {
            1: "Movie Newbie",
            2: "Film Fanatic",
            3: "Cinema Connoisseur",
            4: "Reel Royalty",
            5: "Movie Mastermind"
        }

    def __init__(self, email=None, name=None, gender=None, top5list=None):
        """
        Creates a new member and immediately processes their films.
        """
        self.email = email
        self.name = name
        self.gender = gender
        self.username = self._generate_username()
        
        self.top_5_films = []
        self.favourite_genre = []
        
        self.collected_keywords = [] 
        self.vibe = "Undetermined"

        self.points = randint(100, 1000)  # Random points for fun
        self.level = self.points // 200  # Level based on points
        self.rank = self.ranks.get(self.level, "Movie Newbie")  # Rank based on level
        
        self.cluster_tribe = None  # hmmm
        self.average_year = 0
        self.hipster_score = 0.0
        self.perceived_quality = 0.0

        self.genre_profile = self.ALL_GENRES.copy()
        self.genre_scores = {k: 0.0 for k in self.ALL_GENRES}
        self.pending_list = list(top5list) if top5list else []

        # Start the processing immediately
        self.set_top_5_films()

    def _generate_username(self):
        """
        Creates a unique username using the name and current time.
        """
        prefix = self.name[:3].lower()
        current_time_ms = int(time.time() * 1200)
        time_digits = str(current_time_ms)[-3:]
        return f"{prefix}{time_digits}"

    def update_favourite_genre(self, genre_key, value_change):
        """
        Manually changes the score of a genre and recalculates the favourite.
        """
        if genre_key in self.genre_profile:
            self.genre_profile[genre_key] += value_change
            self._calculate_favourite_genre()
        else:
            print(f"Genre '{genre_key}' not found.")
    
    def update_vibe(self, user_input_text):
        """
        Updates the user's vibe based on a description they type.
        """
        new_vibe = match_vibe_input(user_input_text)
        print(f"Updating vibe from '{self.vibe}' to '{new_vibe}' based on input '{user_input_text}'")
        self.vibe = new_vibe

    def _calculate_favourite_genre(self):
        """
        Finds which genre has the highest count.
        """
        if not self.genre_profile:
            self.favourite_genre = []
            return
        highest_count = max(self.genre_profile.values())
        if highest_count == 0:
            self.favourite_genre = []
            return
        self.favourite_genre = [
            genre for genre, count in self.genre_profile.items() 
            if count == highest_count
        ]

    def _process_film_result(self, best_match):
        """
        Saves the stats and genres for a single confirmed film.
        """
        self.top_5_films.append(best_match.title)
        
        for g_id in best_match.genre_ids:
            genre_name = GENRE_ID_MAP.get(g_id)
            if genre_name in self.genre_profile:
                self.genre_profile[genre_name] += 1
                self.genre_scores[genre_name] += best_match.popularity

        stats = {
            'release_year': int(best_match.release_date[:4]) if best_match.release_date else 0,
            'popularity': best_match.popularity,
            'vote_average': best_match.vote_average
        }
        return stats

    def set_top_5_films(self, api_key=API_KEY):
        """
        Loops through the list (or asks user) until 5 films are verified.
        """
        if not api_key:
            print("Error: No API key provided.")
            return

        total_release_year = 0
        total_film_popularity = 0.0
        total_vote_average = 0.0
        valid_films_count = 0

        print(f"\nHello {self.name}, processing your films...")

        while valid_films_count < 5:
            if self.pending_list:
                film_name = self.pending_list.pop(0)
                print(f"Verifying title choice: {film_name}")
            else:
                film_name = input(f"Enter film #{valid_films_count + 1}: ")

            data = search_film(film_name, api_key)
            match_confirmed = False

            if data and data.results:
                best_match = data.results[0]
                
                # Get details (Director + Keywords)
                director_name, film_keywords = get_movie_details(best_match.id, api_key)
                
                # Case-insensitive match check
                if best_match.title.lower() == film_name.lower():
                    match_confirmed = True
                    print(f"   -> Exact Match: {best_match.title}")
                else:
                    release_year = best_match.release_date[:4] if best_match.release_date else "Unknown"
                    print(f"   -> Found: {best_match.title} ({release_year}), Director: {director_name}")
                    user_response = input("      Is this what you mean? (yes/no): ")
                    if user_response.lower() in ['yes', 'y']:
                        match_confirmed = True
                    else:
                        print("   -> Rejected. Retrying this slot.")
                
                if match_confirmed:
                    # 1. Process standard stats
                    stats = self._process_film_result(best_match)
                    total_release_year += stats['release_year']
                    total_film_popularity += stats['popularity']
                    total_vote_average += stats['vote_average']
                    
                    # 2. Store Keywords
                    self.collected_keywords.extend(film_keywords)
                    
                    valid_films_count += 1
            else:
                print("   -> Film not found.")

        # Final Calculations
        if valid_films_count > 0:
            self.average_year = int(total_release_year / valid_films_count)
            self.hipster_score = round(total_film_popularity / valid_films_count, 2)
            self.perceived_quality = round(total_vote_average / valid_films_count, 1)

        self._calculate_favourite_genre()
        
        self.vibe = calculate_dominant_vibe(self.collected_keywords)

        # Output
        print("-" * 30)
        
        if len(self.favourite_genre) > 1:
            formatted_genres = ", ".join(self.favourite_genre[:-1]) + " and " + self.favourite_genre[-1]
            print(f"Your most popular genres are: {formatted_genres}")
        elif len(self.favourite_genre) == 1:
            print(f"Your favourite genre is: {self.favourite_genre[0]}")
        else:
            print("Your favourite genre is: Undetermined")
            
        print(f"Your Vibe: {self.vibe}")
        print(f"Average Year: {self.average_year}")
        print(f"Hipster Score: {self.hipster_score}")
        print(f"Perceived Quality: {self.perceived_quality}")

    # def save_to_database(self, filename="moviever_PoC.csv"):
    #     """
    #     Saves the user to a CSV file. Auto-generates an ID.
    #     """
    #     import pandas as pd
    #     import os

    #     fav_genre_str = self.favourite_genre[0] if self.favourite_genre else "Undetermined"

    #     new_data = {
    #         "Username": self.username,
    #         "Name": self.name,
    #         "Email": self.email,
    #         "Gender": self.gender,
    #         "Average Year": self.average_year,
    #         "Hipster Score": self.hipster_score,
    #         "Perceived Quality": self.perceived_quality,
    #         "Favourite Genre": fav_genre_str,
    #         "Vibe": self.vibe
    #     }

    #     if os.path.exists(filename):
    #         try:
    #             existing_df = pd.read_csv(filename)
    #             if not existing_df.empty:
    #                 next_id = existing_df["ID"].max() + 1
    #             else:
    #                 next_id = 1
    #         except Exception:
    #             next_id = 1
    #     else:
    #         next_id = 1

    #     new_data["ID"] = next_id
    #     new_df = pd.DataFrame([new_data])
        
    #     mode = 'a' if os.path.exists(filename) else 'w'
    #     header = not os.path.exists(filename)
        
    #     new_df.to_csv(filename, mode=mode, header=header, index=False)
    #     print(f"User saved to '{filename}' with ID: {next_id}")

    def determine_cluster_tribe(self):
        pass

if __name__ == "__main__":
    jason_darby = MovieverMember(
        email="jason@digitaal.com",
        name="Jason",
        gender="Male",
        #top5list=["Melancholia", "Manchester by the Sea", "Lost in Translation", "Blue Valentine", "Eternal Sunshine of the Spotless Mind"]
        top5list=["The Lion King", "Beauty and the Beast", "Aladdin", "Frozzen", "Encanto"] 
        #top5list=["Upgrade", "Dredd", "Strange Days", "Alita: Battle Angel", "RoboCop"]
        #top5list=["Oslo, August 31st", "Before Sunrise", "Victoria", "Irreversible", "Simon Killer"]
    )


    # We no longer need to call set_top_5_films() manually!

    print("You're Key")
    print(API_KEY)
    
    print("\n--- DEBUG: Checking Profile After Processing ---")
    print(jason_darby.genre_profile)
    
    jason_darby.update_favourite_genre("Drama", -1)
    
    print(f"Your initial vibe is: {jason_darby.vibe}")

    print(get_tmdb_recommendations(jason_darby.vibe, api_key=API_KEY, excluded_film_ids=jason_darby.top_5_films)
)

    # print(f"Your new vibe is: {jason_darby.vibe}")
