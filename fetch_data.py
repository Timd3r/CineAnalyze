import os
import json
import time
import requests
from dotenv import load_dotenv

# read the .env file
load_dotenv() 

# pull the secret token into a variable
BEARER_TOKEN = os.getenv("TMDB_BEARER_TOKEN")

if not BEARER_TOKEN:
    raise ValueError("Error: TMDB_BEARER_TOKEN not found in .env file!")

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        if (response.status_code == 200):
            response_json = response.json()
            return response_json
        else:
            print(f"Failed to fetch movie details for ID {movie_id}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred while fetching movie details for ID {movie_id}: {e}")
        return None

def build_entertainment_pipeline(pages=3):
    url = "https://api.themoviedb.org/3/discover/movie"
    all_movies = []
    all_genres = {}

    movie_ids = []
    for page in range(1, pages + 1):
        if page % 10 == 0 or page == pages:
            print(f"Fetching page {page}/{pages}...")
        params = {
            "include_adult": "false",
            "language": "en-US",
            "page": page,
            "sort_by": "popularity.desc",
            "vote_count.gte": 100
        }

        response = requests.get(url, headers=HEADERS, params=params)
        results = None
        if response.status_code == 200:
            results = response.json().get("results", [])
            for movie in results:
                movie_ids.append(movie["id"])
        time.sleep(0.25)
    
    for i, id in enumerate(movie_ids):
        details = fetch_movie_details(id)
        if details:
            if details.get("budget", 0) > 0 and details.get("revenue", 0) > 0:
                all_movies.append(details)
                for genre in details.get("genres", []):
                    all_genres[genre["id"]] = genre["name"]
        
        if (i + 1) % 10 == 0 or (i + 1) == len(movie_ids):
            print(f"Processed {i + 1}/{len(movie_ids)} movies.")
        time.sleep(0.25)
    
    os.makedirs("data", exist_ok=True)
    with open("data/movies.json", "w") as f:
        json.dump(all_movies, f, indent=4, ensure_ascii=False)
    
    with open("data/genres.json", "w") as f:
        json.dump(all_genres, f, indent=4, ensure_ascii=False)
    
    print(f"Fetched {len(all_movies)} movies and {len(all_genres)} genres. Data saved in 'data' directory.")


if __name__ == "__main__":
    build_entertainment_pipeline(pages=150)