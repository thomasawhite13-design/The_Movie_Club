import numpy as np
import requests
import random

# Global cache variables to store the model and embeddings after the first load
_model_cache = None
_vibe_embeddings_cache = None

# These text blocks are used by the AI to understand the "feeling" of the request.
VIBE_DEFINITIONS = {
    "Adrenaline Rush": "martial arts karate kung fu fighting action combat fast paced chase violence explosion survival intense physical warrior car chase shootout",
    
    "Neon Dystopia": "cyberpunk high tech low life ai artificial intelligence cyborg robot neon dystopia hacker virtual reality matrix future sci-fi android futuristic biotech",
    
    "Noir Shadows": "noir neo-noir detective crime shadow murder investigation mystery dark cynical police corruption femme fatale grim bleak moody retro smoke rain",
    
    "Heartfelt": "feel good happy uplifting inspiring friendship funny optimism heartwarming success triumph musical dance singing comedy love romance wholesome family",
    
    "Melancholic": "melancholy sad sadness depression grief loss lonely isolation suicide crying tearjerker emotional heartbreak existential despair gloomy miserable hopeless",
    
    "High Tension": "tense suspense thriller anxiety danger chase hostage trap survival fear panic psychological pressure nervous stressed edge of seat nail biter intense",
    
    "Mind-Bending": "surrealism mindfuck psychology dream hallucination time travel alternate reality puzzle mystery confusing philosophical weird strange trippy crazy complex",
    
    "Horror": "horror scary gore blood monster ghost demon spirit possession haunting slasher killer violence fear death disturbed terrified creepy nightmare shocking",
    
    "Epic Scale": "epic war battle history kingdom empire sword hero legend myth adventure scale army huge grand legendary heroic sweeping massive spectacular fantasy",
    
    "Whimsical": "whimsical magic fantasy fairy tale childhood imagination wonder quirky colorful family musical cute dreamy fun playful childlike innocent"
}

# Genres: 28=Action, 12=Adventure, 878=SciFi, 80=Crime, 9648=Mystery, 35=Comedy, 10749=Romance, 
# 18=Drama, 53=Thriller, 27=Horror, 14=Fantasy, 10752=War, 16=Animation
TMDB_MAPPING = {
    "Adrenaline Rush": {"genres": "28|12", "keywords": None}, 
    "Neon Dystopia": {"genres": "878", "keywords": "4563|222|9882"}, # cyberpunk | ai | neo-noir
    "Noir Shadows": {"genres": "80|9648", "keywords": "9882|10031"}, # neo-noir | detective
    "Heartfelt": {"genres": "35|10749|10751", "keywords": None},
    "Melancholic": {"genres": "18", "keywords": "18035|9799"}, # tragedy | romantic drama
    "High Tension": {"genres": "53", "keywords": None},
    "Mind-Bending": {"genres": "9648|878", "keywords": "10051|11100|321"}, # heist | time travel | mystery
    "Horror": {"genres": "27", "keywords": None},
    "Epic Scale": {"genres": "12|14|10752", "keywords": None},
    "Whimsical": {"genres": "16|14", "keywords": None},
    "Eclectic/Undetermined": {"genres": None, "keywords": None} # Search broadly
}

def get_model_and_embeddings(vibe_definitions):
    """
    Lazy loads the SentenceTransformer model and pre-computes vibe embeddings.
    Checks the global cache to prevent re-loading on every call.
    """
    global _model_cache, _vibe_embeddings_cache
    
    if _model_cache is not None:
        return _model_cache, _vibe_embeddings_cache

    from sentence_transformers import SentenceTransformer
    
    # Load the model (this takes a moment the first time)
    _model_cache = SentenceTransformer('all-MiniLM-L6-v2')
    
    vibe_texts = list(vibe_definitions.values())
    _vibe_embeddings_cache = _model_cache.encode(vibe_texts, convert_to_tensor=True)
    
    return _model_cache, _vibe_embeddings_cache

def calculate_dominant_vibe(raw_keywords_list):
    """
    Matches a list of user keywords to the closest Vibe Definition using 
    semantic similarity. Returns 'Eclectic/Undetermined' if confidence is low.
    """
    if not raw_keywords_list:
        return "Eclectic/Undetermined"

    user_text = " ".join(raw_keywords_list)
    from sentence_transformers import util
    
    model, vibe_embeddings = get_model_and_embeddings(VIBE_DEFINITIONS)
    user_embedding = model.encode(user_text, convert_to_tensor=True)
    cosine_scores = util.cos_sim(user_embedding, vibe_embeddings)
    
    best_score_idx = cosine_scores.argmax()
    best_score = cosine_scores[0][best_score_idx].item()
    
    vibe_labels = list(VIBE_DEFINITIONS.keys())
    
    # Threshold determines how strict the matching is
    if best_score < 0.2: 
        return "Eclectic/Undetermined"
        
    return vibe_labels[best_score_idx]

def get_tmdb_recommendations(vibe_key, api_key, excluded_film_ids=None):
    """
    Queries TMDB based on the mapped vibe key.
    - Fetches high-rated films (vote_average >= 5).
    - Sorts by popularity to ensure relevance.
    - Randomly samples 5 films from the top results.
    - Excludes films listed in excluded_film_ids.
    - Returns a formatted string of titles.
    """
    if excluded_film_ids is None:
        excluded_film_ids = []

    mapping = TMDB_MAPPING.get(vibe_key, TMDB_MAPPING["Eclectic/Undetermined"])
    
    average_vote = 5.0
    minimum_vote_count = 150

    params = {
        "api_key": api_key,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "vote_average.gte": average_vote,
        "vote_count.gte": minimum_vote_count,
        "page": random.randint(1, 3)
    }
    
    if mapping["genres"]:
        params["with_genres"] = mapping["genres"]
    if mapping["keywords"]:
        params["with_keywords"] = mapping["keywords"]

    try:
        response = requests.get("https://api.themoviedb.org/3/discover/movie", params=params)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        
        # Filter out excluded films
        valid_results = [
            movie for movie in results 
            if movie["title"] not in excluded_film_ids
        ]
        
        # Select films
        final_selection = []
        if len(valid_results) >= 5:
            final_selection = random.sample(valid_results, 5)
        else:
            final_selection = valid_results

        if not final_selection:
            return "The Movie Club recommend: No matching films found this time."

        # Extract titles and format string
        titles = [movie["title"] for movie in final_selection]
        return titles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from TMDB: {e}")
        return "The Movie Club recommend: Error connecting to database."

def match_vibe_input(user_input):
    """
    Takes a direct user input string and matches it to the closest Vibe.
    """
    return calculate_dominant_vibe([user_input])