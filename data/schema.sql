-- Table for Genres
CREATE TABLE genres (
    genre_id INT PRIMARY KEY,
    genre_name VARCHAR(100)
);

-- Table for Movies
CREATE TABLE movies (
    movie_id INT PRIMARY KEY,
    title VARCHAR(255),
    budget BIGINT,
    revenue BIGINT,
    release_date DATE,
    runtime INT,
    vote_average DECIMAL(3, 1)
);

-- Junction Table (Many-to-Many relationship)
CREATE TABLE movie_genres (
    movie_id INT REFERENCES movies(movie_id),
    genre_id INT REFERENCES genres(genre_id),
    PRIMARY KEY (movie_id, genre_id)
);