import os
import math
from flask import Flask, render_template, request, abort, jsonify
from flask_caching import Cache
from flask_compress import Compress
from dotenv import load_dotenv
import pandas as pd

from recommender import HybridRecommender

load_dotenv()
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
if not TMDB_API_KEY:
    print("WARNING: TMDB_API_KEY not set in .env. Poster fetching was already done offline.")

app = Flask(__name__)

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

compress = Compress(app)
@app.after_request
def set_cache_headers(response):
    """
    Tell browsers (and any CDN) to cache static files for 30 days.
    Only apply this to static assets (css, js, images).
    """
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=2592000'
    return response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'dataset', 'tmdb_dataset.csv')

df = pd.read_csv(DATA_PATH)

df['id'] = pd.to_numeric(df['id'], errors='coerce').astype(int)
df['poster_id'] = pd.to_numeric(df['poster_id'], errors='coerce').astype(int)

def _make_genres_display(x):
    if isinstance(x, list):
        return ", ".join(x)
    try:
        parsed = eval(x) if isinstance(x, str) else []
        if isinstance(parsed, list):
            return ", ".join(parsed)
    except Exception:
        pass
    return str(x)

df['genres_display'] = df['genres'].apply(_make_genres_display)

recommender = HybridRecommender(df)

@app.route('/')
def home():
    """
    Home page: paginated list of all movies (including poster_url).
    """
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_movies = len(df)
    total_pages = max(1, math.ceil(total_movies / per_page))

    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = min(start + per_page, total_movies)

    movies_page = df.iloc[start:end].to_dict('records')

    pagination_start = max(1, page - 2)
    pagination_end = min(total_pages, page + 2)
    if (pagination_end - pagination_start) < 4:
        pagination_start = max(1, min(pagination_start, total_pages - 4))
        pagination_end = min(total_pages, pagination_start + 4)
    pagination_pages = list(range(pagination_start, pagination_end + 1))

    return render_template(
        'index.html',
        movies=movies_page,
        page=page,
        total_pages=total_pages,
        pagination_pages=pagination_pages
    )


@app.route('/search', methods=['GET'])
def search():
    """
    Search endpoint: returns JSON array of {id, title_x} for movies whose title_x
    contains the query substring (case-insensitive).
    """
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify([])

    matching = df[df['title_x'].str.lower().str.contains(query, na=False)]
    results = matching[['id', 'title_x']].rename(columns={'title_x': 'title'}).to_dict(orient='records')
    return jsonify(results)


@cache.memoize(timeout=300)
@app.route('/recommend/<int:movie_id>')
def recommend(movie_id):
    """
    Recommendations page: shows top - 10 similar movies based on precomputed matrix.
    Cached for 300 seconds (5 minutes) to avoid recomputing on every hit.
    """
    if movie_id not in recommender.indices:
        abort(404, description=f"Movie ID {movie_id} not found.")

    recs_df = recommender.get_recommendations(movie_id)

    recs = recs_df.to_dict('records')

    movie_row = df.loc[df['id'] == movie_id]
    movie_title = movie_row['title_x'].iloc[0] if not movie_row.empty else "Unknown"

    return render_template(
        'recommendations.html',
        movie_title=movie_title,
        recommendations=recs
    )

if __name__ == '__main__':
    debug_flag = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_flag)
