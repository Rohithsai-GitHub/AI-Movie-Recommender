import requests
import pandas as pd


class TMDBHelper:
    """
    Simplified helper that fetches posters from TMDB’s “Get Movie Images” endpoint:
      https://api.themoviedb.org/3/movie/{movie_id}/images

    Usage:
        tmdb = TMDBHelper(api_key="YOUR_KEY")
        poster_url = tmdb.get_poster_url(poster_id)
    """

    MOVIE_IMAGES_URL = "https://api.themoviedb.org/3/movie/{movie_id}/images"
    IMG_BASE_URL = "https://image.tmdb.org/t/p/w500"

    def __init__(self, api_key: str):
        if not api_key or not isinstance(api_key, str):
            raise ValueError("TMDB API key is required.")
        self.api_key = api_key
        self.poster_cache = {}

    def get_poster_url(self, poster_id: int) -> str:
        """
        Return the full poster URL for the given poster_id.
        - If cached, returns immediately.
        - Otherwise, fetch /movie/{poster_id}/images, grab the first 'file_path', and build the URL.
        - If any error or no posters exist, returns None.
        """
        if poster_id in self.poster_cache:
            return self.poster_cache[poster_id]

        url = TMDBHelper.MOVIE_IMAGES_URL.format(movie_id=poster_id)
        try:
            response = requests.get(url, params={"api_key": self.api_key}, timeout=10)
            if response.status_code != 200:
                print(f"[TMDBHelper] HTTP {response.status_code} for poster_id {poster_id}: {response.text}")
                self.poster_cache[poster_id] = None
                return None

            data = response.json()
            posters = data.get("posters")
            if not posters:
                self.poster_cache[poster_id] = None
                return None

            file_path = posters[0].get("file_path")
            if not file_path:
                self.poster_cache[poster_id] = None
                return None

            full_url = f"{TMDBHelper.IMG_BASE_URL}{file_path}"
            self.poster_cache[poster_id] = full_url
            return full_url

        except requests.RequestException as e:
            print(f"[TMDBHelper] RequestException for poster_id {poster_id}: {e}")
            self.poster_cache[poster_id] = None
            return None

    def add_poster_urls(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Given a DataFrame with a 'poster_id' column, add 'poster_url':
        (PROFILE NOTE: In our app, we call get_poster_url() manually on df['poster_id'] 
         rather than using this helper. But it’s here in case you want to apply to an entire DataFrame.)
        """
        df = df.copy()
        df['poster_url'] = df['poster_id'].apply(self.get_poster_url)
        return df
