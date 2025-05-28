[![Movie Recommendation System ...](https://images.openai.com/thumbnails/93ffea57647b82c263515337decb7c80.jpeg)](https://medium.com/%40akriti.upadhyay/how-to-create-a-vector-based-movie-recommendation-system-using-qdrant-db-e026554f49ec)

---

## 📄 README: Movie Recommendation System

# 🎬 Movie Recommendation System

**Author:** Rohith Sai
**License:** MIT
**Repository:** [GitHub Link](https://github.com/Rohithsai-GitHub/Movie-Recommendation-System)

---

### 🚀 Project Overview

This project is a content-based movie recommendation system that suggests the top 5 movies based on user preferences. It leverages the MovieLens dataset and is built using Python, Flask, and essential data science libraries.

---

### 🧠 Key Features

* **Content-Based Filtering:** Utilizes movie metadata to compute similarities and recommend movies.
* **Interactive Web Interface:** Built with Flask to provide a user-friendly interface for movie recommendations.
* **Scalable Architecture:** Designed to handle larger datasets by simply replacing the existing dataset.
* **Modular Codebase:** Clean and modular code structure for easy maintenance and scalability.

---

### 🛠️ Tech Stack

* **Frontend:** HTML, CSS (via Flask templates)
* **Backend:** Python, Flask
* **Data Processing:** Pandas, NumPy
* **Machine Learning:** Scikit-learn
* **Data Source:** [MovieLens Dataset](https://grouplens.org/datasets/movielens/)

---

### 📂 Project Structure

```
├── app.py
├── templates/
│   └── index.html
├── static/
│   └── styles.css
├── data/
│   └── ml-latest-small/
├── requirements.txt
└── README.md
```

---

### ⚙️ Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Rohithsai-GitHub/Movie-Recommendation-System.git
   cd Movie-Recommendation-System
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare the Dataset:**

   * Download the [MovieLens dataset](https://grouplens.org/datasets/movielens/).
   * Extract it and place it inside the `data/` directory.

4. **Run the Application:**

   ```bash
   python app.py
   ```

   * Navigate to `http://127.0.0.1:5000/` in your browser to use the application.

---

**Understanding Content-Based Filtering:**

Content-based filtering recommends items similar to those a user has liked in the past. It relies on item features and user preferences, making it effective for new users with limited interaction history.

**Implementation Highlights:**

1. **Data Preprocessing:**

   * Loaded and cleaned the dataset using Pandas.
   * Extracted relevant features such as genres, directors, and cast.

2. **Feature Extraction:**

   * Converted textual data into numerical vectors using techniques like TF-IDF.

3. **Similarity Computation:**

   * Calculated cosine similarity between movie vectors to identify similar movies.

4. **Web Application:**

   * Created routes in Flask to handle user inputs and display recommendations.

---

### 📈 Future Enhancements

* **Incorporate Collaborative Filtering:** To improve recommendation accuracy by considering user behaviors.
* **Implement Hybrid Models:** Combine content-based and collaborative filtering for better results.
* **Enhance UI/UX:** Improve the frontend for a more engaging user experience.
* **Deploy Application:** Host the application using platforms like Heroku or AWS.

---

### 🤝 Contributions

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

---

### 📬 Contact

For any queries or suggestions, feel free to reach out via [LinkedIn](https://www.linkedin.com/in/rohithsaikommana/) or open an issue in the repository.

---
