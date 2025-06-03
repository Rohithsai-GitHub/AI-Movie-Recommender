import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import ast
import numpy as np

class HybridRecommender:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

        if self.df['id'].duplicated().any():
            raise ValueError("Duplicate IDs found in dataset. IDs must be unique.")

        self.indices = pd.Series(self.df.index, index=self.df['id']).to_dict()
        self.tfidf = TfidfVectorizer(stop_words='english', max_features=10000, min_df=5)
        self.similarity_matrix = None
        self._create_similarity_matrix()

    def _safe_convert(self, x):
        if isinstance(x, list):
            return x
        if pd.isna(x) or not isinstance(x, str) or x.strip() == "":
            return []
        try:
            parsed = ast.literal_eval(x)
            if isinstance(parsed, list):
                if parsed and isinstance(parsed[0], dict) and 'name' in parsed[0]:
                    return [item.get('name') for item in parsed if isinstance(item, dict)]
                return [str(item) for item in parsed]
        except (ValueError, SyntaxError):
            stripped = x.strip()
            if stripped.startswith('[') and stripped.endswith(']'):
                inner = stripped[1:-1].strip()
                if inner:
                    return [token.strip().strip("'\"") for token in inner.split(',')]
        return [str(x)]

    def _create_feature_soup(self, row):
        genres_list = self._safe_convert(row.get('genres', []))
        genres_text = " ".join(genres_list)

        keywords_list = self._safe_convert(row.get('keywords', []))
        keywords_text = " ".join(keywords_list)

        actors_raw = row.get('actors', "")
        if pd.isna(actors_raw) or not isinstance(actors_raw, str):
            actors_text = ""
        else:
            actors_tokens = [a.strip() for a in actors_raw.split(',') if a.strip()]
            actors_text = " ".join(actors_tokens)

        director_txt = "" if pd.isna(row.get('director')) else str(row.get('director'))
        vote_avg = str(row.get('vote_average', ""))
        popularity = str(row.get('popularity', ""))

        return f"{genres_text} {keywords_text} {actors_text} {director_txt} {vote_avg} {popularity}"

    def _create_similarity_matrix(self):
        self.df['soup'] = self.df.apply(self._create_feature_soup, axis=1)
        tfidf_matrix = self.tfidf.fit_transform(self.df['soup'])
        self.similarity_matrix = linear_kernel(tfidf_matrix, tfidf_matrix)

    def get_recommendations(self, movie_id: int, top_n: int = 10) -> pd.DataFrame:
        if movie_id not in self.indices:
            raise KeyError(f"Movie ID {movie_id} not found.")

        idx = self.indices[movie_id]
        sim_row = self.similarity_matrix[idx]
        top_indices = np.argsort(sim_row)[::-1]
        top_indices = [i for i in top_indices if i != idx][:top_n]

        return self.df.iloc[top_indices].copy()
