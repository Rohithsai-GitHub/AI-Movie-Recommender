import os
from flask import Flask, render_template, send_from_directory, abort, request
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__, static_url_path='/static')

movies = pd.read_csv('data/movies.csv')
ratings = pd.read_csv('data/ratings.csv')

movie_ratings = ratings.pivot_table(index='movieId', columns='userId', values='rating').fillna(0)

cosine_sim = cosine_similarity(movie_ratings)
cosine_sim_df = pd.DataFrame(cosine_sim, index=movie_ratings.index, columns=movie_ratings.index)

def get_recommendations(movie_id, top_n=5):

    if movie_id not in cosine_sim_df.index:
        return []

    sim_scores = cosine_sim_df[movie_id].sort_values(ascending=False)
    similar_movie_ids = sim_scores.index[sim_scores.index != movie_id][:top_n]
    recommendations = movies[movies['movieId'].isin(similar_movie_ids)].to_dict('records')
    return recommendations

def get_movie(movie_id):
    """Fetch the details for a single movie."""
    movie = movies[movies['movieId'] == movie_id]
    if movie.empty:
        return None
    return movie.iloc[0].to_dict()

def get_all_genres(movies_df):
    """Extracts a sorted list of unique genres from the movies dataframe."""
    genres_set = set()
    for genres in movies_df['genres']:
        for genre in genres.split("|"):
            genres_set.add(genre.strip())
    return sorted(genres_set)

all_genres = get_all_genres(movies)

def get_pagination_pages(current_page, total_pages, delta=2):
    """
    Returns a list of page numbers and ellipsis symbols ("...") for pagination.
    For example, if current_page=5 and total_pages=10, the output might be:
    [1, "...", 3, 4, 5, 6, 7, "...", 10]
    """
    pages = []
    if total_pages <= 1:
        return pages

    pages.append(1)

    start = max(2, current_page - delta)
    end = min(total_pages - 1, current_page + delta)

    if start > 2:
        pages.append("...")

    for p in range(start, end + 1):
        pages.append(p)

    if end < total_pages - 1:
        pages.append("...")

    if total_pages > 1:
        pages.append(total_pages)
    return pages

@app.route('/')
def index():
    """
    Homepage route: Supports search functionality (using GET parameter 'q'), filtering by genre,
    and paginates the movies in card style, showing 20 movies per page.
    """
    query = request.args.get('q', '')
    genre_filter = request.args.get('genre', '')
    try:
        page = int(request.args.get('page', '1'))
    except ValueError:
        page = 1

    PER_PAGE = 20

    filtered_movies = movies

    if query:
        filtered_movies = filtered_movies[
            filtered_movies['title'].str.contains(query, case=False, na=False)
        ]

    if genre_filter:
        filtered_movies = filtered_movies[
            filtered_movies['genres'].str.contains(genre_filter, case=False, na=False)
        ]

    total_movies = len(filtered_movies)
    total_pages = (total_movies + PER_PAGE - 1) // PER_PAGE

    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    movies_page = filtered_movies.iloc[start:end].to_dict('records')

    pagination_pages = get_pagination_pages(page, total_pages)

    return render_template(
        'index.html',
        movies=movies_page,
        query=query,
        genre_filter=genre_filter,
        all_genres=all_genres,
        page=page,
        total_pages=total_pages,
        pagination_pages=pagination_pages
    )

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    """
    Movie detail page: Streams the movie (if available) and shows recommendations.
    """
    movie = get_movie(movie_id)
    if not movie:
        abort(404)

    recommendations = get_recommendations(movie_id)
    video_filename = f"movie_{movie_id}.mp4"
    video_path = os.path.join(app.static_folder, 'videos', video_filename)
    video_exists = os.path.exists(video_path)

    return render_template(
        'movie.html',
        movie=movie,
        recommendations=recommendations,
        video_filename=video_filename if video_exists else None
    )

@app.route('/videos/<path:filename>')
def video(filename):
    """Serve video files from the static/videos directory."""
    return send_from_directory(os.path.join(app.static_folder, 'videos'), filename)

if __name__ == '__main__':
    app.run(debug=True)
