import json
import psycopg2 # The driver for PostgreSQL
from psycopg2.extras import execute_values

def migrate_data():
    # Connect to your database
    # Update these values with your actual DB credentials
    conn = psycopg2.connect(
        dbname="movie_db", 
        user="tde-raev", 
        password="Password", 
        host="localhost", 
        port="5432"
    )
    cur = conn.cursor()

    # Load the JSON data
    with open("data/movies.json", "r") as f:
        movies = json.load(f)

    with open("data/genres.json", "r") as f:
        genres_dict = json.load(f)

    genre_tuples = [(int(g_id), g_name) for g_id, g_name in genres_dict.items()]
    genre_query = "INSERT INTO genres (genre_id, genre_name) VALUES %s ON CONFLICT DO NOTHING;"
    execute_values(cur, genre_query, genre_tuples)

    movie_tuples = []
    movie_genre_tuples = []

    for movie in movies:
        # Prepare movie core data
        movie_tuples.append((
            movie['id'], 
            movie['title'], 
            movie['budget'], 
            movie['revenue'], 
            movie['release_date'], 
            movie['runtime'], 
            movie['vote_average']
        ))
        
        # Prepare junction links
        for genre in movie['genres']:
            movie_genre_tuples.append((movie['id'], genre['id']))

    # Execute Movie Bulk Load
    movie_query = """
        INSERT INTO movies (movie_id, title, budget, revenue, release_date, runtime, vote_average)
        VALUES %s ON CONFLICT (movie_id) DO NOTHING;
    """
    execute_values(cur, movie_query, movie_tuples)

    junction_query = "INSERT INTO movie_genres (movie_id, genre_id) VALUES %s ON CONFLICT DO NOTHING;"
    execute_values(cur, junction_query, movie_genre_tuples)

    conn.commit()
    
    cur.close()
    conn.close()
    print("Data successfully migrated to PostgreSQL!")

if __name__ == "__main__":
    migrate_data()