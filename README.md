# AI Movie Recommender

A fast, production‐ready web application that suggests movies similar to any title you provide. Powered by a content‐based hybrid recommendation algorithm, this app leverages movie metadata (genres, keywords, cast, director, popularity) to generate personalized movie recommendations in milliseconds.

---

## Table of Contents

1. [Demo](#demo)  
2. [Features](#features)  
3. [Technology Stack](#technology-stack)  
4. [Getting Started](#getting-started)  
   1. [Prerequisites](#prerequisites)  
   2. [Installation](#installation)
   3. [Data Preparation](#data-preparation)
   4. [Running Locally](#running-locally)
5. [Project Structure](#project-structure)
6. [Code Overview](#code-overview)
   1. [`app.py`](#app-py)
   2. [`recommender.py`](#recommender-py)
   3. [`get_posters.py`](#get-posters-py)
   4. [`tmdb_helper.py`](#tmdb-helper-py)
   5. [`templates/`](#templates) 
7. [Configuration & Environment Variables](#configuration--environment-variables)  
8. [Deployment](#deployment-rendercom)  
9. [Performance & Optimizations](#performance--optimizations)  
10. [Future Enhancements](#future-enhancements)  
11. [License](#license)  
12. [Acknowledgments](#acknowledgments)

---

## Demo

Visit the live demo: **[AI Movie Recommender](https://movierecommender-zrtf.onrender.com/)**  

---

## Features

- **Instant Search**: Type any movie title—live suggestions appear as you type.  
- **Personalized Recommendations**: Click “View Similar” to see 10 movies most like your chosen title.  
- **Movie Posters**: Each movie card shows a high‐resolution poster (fetched from TMDB).  
- **Caching**: Recommendations are cached for 5 minutes, guaranteeing sub‐200 ms response times.  
- **GZIP Compression**: All HTML/JSON responses are compressed, minimizing bandwidth usage.  
- **Responsive Design**: Built on Bootstrap 5—looks great on desktop, tablet, and mobile.  
- **Production‐Ready**: Runs under Gunicorn with environment‐based configuration, ready for Render.com, Heroku, or any WSGI host.

---

## Technology Stack

- **Backend**:  
  - Python 3.9+  
  - Flask (web framework)  
  - Flask‐Caching (memoization)  
  - Flask‐Compress (GZIP compression)  
  - Pandas (data manipulation)  
  - scikit‐learn (TF-IDF vectorization & cosine similarity)  
  - Requests (HTTP requests to TMDB, used in offline script)

- **Frontend**:  
  - HTML5 templating  
  - Bootstrap 5 (responsive CSS)  
  - Vanilla JavaScript (search autocomplete)

- **Data Sources**:  
  - [The Movie Database (TMDB) API](https://developers.themoviedb.org/3) for movie metadata & poster images  
  - Custom cleaned CSVs:  
    - `tmdb_dataset.csv` with TMBD data and poster urls.

---

## Getting Started

### Prerequisites

Before you begin, make sure you have:

- **Python 3.9+** installed  
- A valid **TMDB API key** (sign up at [themoviedb.org](https://www.themoviedb.org/)) - Note: Sometimes TMDB won't work with some Wifi-networks. You can change your network or use without movie posters.

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Rohithsai-GitHub/AI-Movie-Recommender.git
   cd AI-Movie-Recommender
   ````

2. **Create & Activate a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   * create a new `.env` file in the project root.
   * Add your TMDB API key:

     ```
     TMDB_API_KEY=your_real_tmdb_api_key_here
     ```

---

## Running Locally

Once you have `tmdb_dataset.csv` ready in dataset:

```bash
python app.py
```

By default, the Flask development server runs on `http://127.0.0.1:5000/`. Visit that URL to see:

* **Home Page**: Search box + paginated movie grid with posters.
* **Recommendations Page**: Click any “View Similar” to get 10 related titles, with posters.

---

## Project Structure

```
AI-Movie-Recommender/
├─ app.py                         # Main Flask application
├─ get_posters.py                 # Offline script to build poster_url column for understanding purpose
├─ recommender.py                 # HybridRecommender (TF-IDF + Cosine Similarity)
├─ tmdb_helper.py                 # (Legacy; offline use or reference)
├─ .env                           # Contains TMDB_API_KEY
├─ requirements.txt               # Python dependencies (Flask, Pandas, scikit-learn, caching, compress)
├─ dataset/
│   └─ tmdb_dataset.csv           # Pre-cleaned
├─ static/
│   └─ css/
│       └─ style.css             # Custom CSS for cards, pagination, etc.
└─ templates/
    ├─ index.html                # Homepage (search + paginated movies)
    └─ recommendations.html      # Recommendations page (top-10 similar movies)
```

---

## Code Overview

### `app.py`

* **Imports** environment via `python-dotenv` and sets up Flask, Flask-Caching, Flask-Compress.
* **Loads** `tmdb_dataset_with_posters.csv` (no runtime TMDB calls).
* **Routes**:

  * `/` (home): Shows paginated movie grid; uses `poster_url` from DataFrame.
  * `/search`: Returns JSON array of `{id, title}` for titles containing the query.
  * `/recommend/<movie_id>`: Returns top‐10 recommendations and caches results for 5 minutes.

### `recommender.py`

* **`HybridRecommender` class**:

  * Takes a DataFrame with movie metadata.
  * Builds a text “soup” combining genres, keywords, cast, director, and numeric features.
  * Vectorizes with TF-IDF and computes a cosine‐similarity matrix on initialization.
  * Method `get_recommendations(movie_id, top_n=10)` returns the top‐N similar movies.

### `get_posters.py`

* **Offline script** that reads `tmdb_dataset_with_poster_id.csv`, loops through each `poster_id`, calls TMDB’s `/movie/{id}/images` endpoint, picks the first poster’s `file_path`, and writes out `poster_url` to `dataset/tmdb_dataset_with_posters.csv`.
* Run once before and rename it to original dataset name for deployment to avoid runtime API calls.

### `templates/`

* **`index.html`**:

  * Uses Bootstrap 5 for responsive grid.
  * Contains a search bar with a live suggestions dropdown.
  * Renders paginated movie cards (300 px tall posters, titles, ratings, genres, “View Similar” button).
  * Includes JavaScript to call `/search` and render results.

* **`recommendations.html`**:

  * Displays 10 recommended movies, each with poster, title, director, rating, and truncated cast.
  * Includes a “Back to Home” button.

## Configuration & Environment Variables

The only environment variable needed for offline data preparation is:

```
TMDB_API_KEY=your_tmdb_api_key
```

Place it in a file named `.env` at the project root. The application itself does not require TMDB API calls at runtime (assuming you’ve already run `get_posters.py`).

---

## Want to Deploy (Render.com)

1. **Add `requirements.txt` & `Procfile`**

   * **`Procfile`** (in project root):

     ```
     web: gunicorn app:app
     ```
2. **Push** your repository to GitHub/GitLab.
3. **Connect** to Render.com:

   * Create a new “Web Service.”
   * Select your repository and branch.
   * Render automatically runs `pip install -r requirements.txt` and picks up the `Procfile` to launch Gunicorn.
4. **Environment Variables**:

   * In Render’s dashboard, set:

     ```
     TMDB_API_KEY = your_tmdb_api_key
     ```
   * (Even though the app no longer fetches posters at runtime, you’ll still need this for offline updates if you ever re‐run `get_posters.py`.)

Once deployed, you’ll see a live URL (e.g. `https://movierecommender-zrtf.onrender.com`). Go ahead and explore—search any movie, click “Watch Similar,” and witness instant, poster‐filled recommendations!

---

## Performance & Optimizations

1. **Offline Poster Pre‐Fetch**

   * All poster URLs are computed once and stored in `tmdb_dataset_with_posters.csv`. No runtime API calls means faster page loads and zero rate‐limit concerns. Note: I have already added poster url's in the provided dataset. Posters.py is for understanding.

2. **Precomputed Similarity Matrix**

   * We build the TF-IDF and cosine‐similarity matrix once when the server boots. Every subsequent recommendation lookup is essentially a Python dictionary lookup (`id → index`) plus a quick `np.argsort` on a vector of length \~4,000. That operation completes in under 5 ms on modern hardware.

3. **Flask‐Caching**

   * Recommendations for each `movie_id` are cached for 5 minutes using simple in‐memory storage. Frequent queries (e.g., “Who’s similar to Inception?”) return instantaneously from cache.

4. **Flask‐Compress (GZIP)**

   * All HTML, JSON, and CSS responses are GZIP‐compressed. This often shrinks payload size by 70–90%, reducing network latency, especially on mobile connections.

5. **Browser Caching**

   * We serve static assets (CSS, JS) with long “Cache-Control” headers, so browsers hold onto them for up to 30 days. Poster images (hosted on TMDB’s CDN) also benefit from far‐future caching.

---

## Future Enhancements

* **User Accounts & Ratings**: Allow users to sign in, rate movies, and receive personalized collaborative filtering recommendations.
* **Dynamic Filters**: Add dropdown filters for genre, release year, or language on the homepage.
* **Collaborative Filtering Augmentation**: Combine content‐based recommendations with collaborative signals (e.g. users who liked Movie A also liked Movie B).
* **Recommendation Explainability**: Show why a movie was recommended (e.g. “Because it shares the same director and genre with your chosen title”).
* **Mobile App / PWA**: Convert into a Progressive Web App so users can “install” the recommender on their phone, receive push notifications for new releases, etc.
* **Real‐Time Data Updates**: Automate nightly or weekly runs of `get_posters.py` and a script to refresh the TF-IDF model so the app stays up to date with the latest TMDB metadata.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Acknowledgments

* **TMDB (The Movie Database)** for providing a rich API and metadata for millions of movies.
* **Pandas / scikit‐learn** communities for their excellent libraries, which make prototyping recommendation engines extremely straightforward.
* **Flask, Flask‐Caching, Flask‐Compress** maintainers for enabling development of production‐grade Python web applications with minimal friction.
* **Bootstrap 5** for a delightful and responsive UI toolkit.

Feel free to open an issue or submit a pull request if you find a bug or want to add a feature. Enjoy discovering your next favorite movie!

---

*Thank you for reading! I hope this helps you understand how to build and optimize a production‐ready AI Movie Recommender. If you found this helpful, consider starring ⭐ the repository and sharing your feedback.*
