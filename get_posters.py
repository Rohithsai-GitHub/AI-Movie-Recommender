
import os
import pandas as pd
import requests
from dotenv import load_dotenv

# ------------------------------------------------------------------------------
# 1) Load TMDB API key from .env
# ------------------------------------------------------------------------------
load_dotenv()
API_KEY = os.getenv('TMDB_API_KEY')
if not API_KEY:
    raise RuntimeError("TMDB_API_KEY not set in .env. Please add your key.")

# ------------------------------------------------------------------------------
# 2) Constants for TMDB endpoints and image base URL (w500 size)
# ------------------------------------------------------------------------------
MOVIE_DETAILS_URL = "https://api.themoviedb.org/3/movie/{movie_id}"
IMG_BASE_URL = "https://image.tmdb.org/t/p/w500"

# ------------------------------------------------------------------------------
# 3) Read the intermediate dataset with 'poster_id'
#    (this CSV should have been created earlier via tmdb_5000 matching)
# ------------------------------------------------------------------------------
INPUT_PATH = os.path.join('dataset', 'tmdb_dataset.csv')
df = pd.read_csv(INPUT_PATH)

# Ensure 'poster_id' is numeric
df['poster_id'] = pd.to_numeric(df['poster_id'], errors='coerce')

# ------------------------------------------------------------------------------
# 4) For each poster_id, call /movie/{id}?api_key=... and extract 'poster_path'.
#    Build full URL as IMG_BASE_URL + poster_path. If poster_path is missing or
#    request fails, store None.
# ------------------------------------------------------------------------------
poster_urls = []
total = len(df)
print(f"Fetching poster URLs for {total} movies...")

for idx, row in df.iterrows():
    poster_id = int(row['poster_id'])
    try:
        # Query the movie details endpoint
        response = requests.get(
            MOVIE_DETAILS_URL.format(movie_id=poster_id),
            params={'api_key': API_KEY},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                # Construct full URL
                full_url = f"{IMG_BASE_URL}{poster_path}"
                poster_urls.append(full_url)
            else:
                poster_urls.append(None)
        else:
            # e.g. 404 Not Found or invalid key
            poster_urls.append(None)

    except requests.RequestException as e:
        # Network issue or timeout
        print(f"Warning: could not fetch poster for ID {poster_id}: {e}")
        poster_urls.append(None)

    # Optional progress indicator
    if (idx + 1) % 500 == 0 or (idx + 1) == total:
        print(f"  → Processed {idx + 1}/{total}")

# ------------------------------------------------------------------------------
# 5) Attach the new 'poster_url' column and save a fresh CSV
# ------------------------------------------------------------------------------
df['poster_url'] = poster_urls
OUTPUT_PATH = os.path.join('dataset', 'tmdb_dataset_with_posters.csv')
df.to_csv(OUTPUT_PATH, index=False)

print(f"\nDone! Wrote {total} rows (with poster_url) to:\n  {OUTPUT_PATH}")
