from os import WCONTINUED

from flask import Flask, request, redirect, url_for, render_template, flash
from data_manager import DataManager
from models import db, Movie, User
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
app = Flask(__name__)
app.secret_key = 'my_secret_key_123' # needed for redirection

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Link the database and the app. This is the reason you need to import db from models
db.init_app(app)

# Create an object of your DataManager class
data_manager = DataManager()


def fetch_movie(title):
    """Fetches data from API based on movie title"""
    URL = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}"

    result = {}
    try:
        res = requests.get(URL)
        if res.ok:
            result = res.json()

    except requests.exceptions.Timeout:
        print("Error: The request to OMDb timed out.")
        return {}

    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the OMDb API "
              "(no internet or server unreachable).")
        return {}

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        return {}

    return result

@app.route('/')
def home():
    """Homepage:
    Shows a list of all registered users and a form for adding new users."""
    users = data_manager.get_users()
    return render_template('index.html', users=users)

@app.route('/users', methods=['POST'])
def create_user():
    """When the user submits the “add user” form, a POST request is made.
    The server receives the new user info, adds it to the database,
    then redirects back to /"""

    name = request.form.get('name')
    data_manager.create_user(name)
    # Redirect, so that the form is empty again
    return redirect(url_for('home'))

@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):
    """When you click on a username,
    the app retrieves that user’s list of favorite movies and displays it."""
    movies = data_manager.get_movies(user_id)
    user = User.query.get(user_id)
    return render_template('movies.html', movies=movies, user=user)

@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """Add a new movie to a user’s list of favorite movies."""
    title = request.form.get('title')
    year = request.form.get('year')
    movies = data_manager.get_movies(user_id)

    movie_to_add_dict = fetch_movie(title)

    # Movie not found in OMDb
    if movie_to_add_dict.get("Response") != "True":
        flash("Movie not found in OMDb.", "error")
        return redirect(url_for('get_movies', user_id=user_id))

    # Checks if the year in user input is the year in OMDb response
    if year:
        if year.strip() != movie_to_add_dict.get("Year"):
            flash("Movie with this title and release year not found in OMDb.",
                  "error")
            return redirect(url_for('get_movies', user_id=user_id))

    new_movie = Movie(name=movie_to_add_dict.get("Title"),
                      director=movie_to_add_dict.get("Director"),
                      year=movie_to_add_dict.get("Year"),
                      poster_url=movie_to_add_dict.get("Poster"),
                      user_id=user_id)

    # Checks if movie already exists in collection
    if new_movie.name in {movie.name for movie in movies}:
        flash("Movie is already in your list.",
              "error")
        return redirect(url_for('get_movies', user_id=user_id))

    data_manager.add_movie(new_movie)

    return redirect(url_for('get_movies', user_id=user_id))

@app.route('/users/<int:user_id>/movies/<int:movie_id>/update',
           methods=['POST'])
def update_movie(user_id, movie_id):
    """Modify the title of a specific movie in a user’s list,
    without depending on OMDb for corrections."""
    new_title = request.form.get('title')
    data_manager.update_movie(movie_id, new_title)

    return redirect(url_for('get_movies', user_id=user_id, movie_id=movie_id))

@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete',
           methods=['POST'])
def delete_movie(user_id, movie_id):
    """Remove a specific movie from a user’s favorite movie list."""
    data_manager.delete_movie(movie_id)
    return redirect(url_for('get_movies', user_id=user_id, movie_id=movie_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
  with app.app_context():
    db.create_all()

  app.run()