import os
import math
from flask import Flask, render_template, request, abort
from dotenv import load_dotenv
import pandas as pd

from recommender import HybridRecommender
from tmdb_helper import TMDBHelper

load_dotenv()  # reads from .env in project root
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY not set in .env. Please add your API key.")

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'dataset', 'tmdb_dataset.csv')

df = pd.read_csv(DATA_PATH)

df['id'] = pd.to_numeric(df['id'], errors='coerce')
df['poster_id'] = pd.to_numeric(df['poster_id'], errors='coerce')

df = df.dropna(subset=['id', 'poster_id']).reset_index(drop=True)
df['id'] = df['id'].astype(int)
df['poster_id'] = df['poster_id'].astype(int)

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
tmdb = TMDBHelper(api_key=TMDB_API_KEY)

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_movies = len(df)
    total_pages = max(1, math.ceil(total_movies / per_page))
    
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = min(start + per_page, total_movies)

    movies_page = df.iloc[start:end].copy()

    movies_page['poster_url'] = movies_page['poster_id'].apply(tmdb.get_poster_url)
    
    pagination_start = max(1, page - 2)
    pagination_end = min(total_pages, page + 2)
    if pagination_end - pagination_start < 4:
        pagination_start = max(1, min(pagination_start, total_pages - 4))
        pagination_end = min(total_pages, pagination_start + 4)
    pagination_pages = list(range(pagination_start, pagination_end + 1))

    return render_template(
        'index.html',
        movies=movies_page.to_dict('records'),
        page=page,
        total_pages=total_pages,
        pagination_pages=pagination_pages
    )


@app.route('/recommend/<int:movie_id>')
def recommend(movie_id):
    if movie_id not in recommender.indices:
        abort(404, description=f"Movie ID {movie_id} not found.")
    
    recs_df = recommender.get_recommendations(movie_id)
    recs_df['poster_url'] = recs_df['poster_id'].apply(tmdb.get_poster_url)

    movie_row = df.loc[df['id'] == movie_id]
    movie_title = movie_row['title_x'].iloc[0] if not movie_row.empty else "Unknown"

    return render_template(
        'recommendations.html',
        movie_title=movie_title,
        recommendations=recs_df.to_dict('records')
    )

if __name__ == '__main__':
    debug_flag = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_flag)
