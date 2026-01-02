from flask import Flask
from data_manager import DataManager
from models import db, Movie
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Link the database and the app. This is the reason you need to import db from models
db.init_app(app)

# Create an object of your DataManager class
data_manager = DataManager()

@app.route('/')
def home():
    """Homepage:
    Shows a list of all registered users and a form for adding new users."""
    return "Welcome to MoviWeb App!"

@app.route('/users', methods=['GET', 'POST'])
def list_users():
    """When the user submits the “add user” form, a POST request is made.
    The server receives the new user info, adds it to the database,
    then redirects back to /"""
    users = data_manager.get_users()
    return str(users)

@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_users_movies(user_id):
    """When you click on a username,
    the app retrieves that user’s list of favorite movies and displays it."""
    pass

@app.route('users/<int:user_id>/movies', methods=['POST'])
def add_movie_to_user(user_id):
    """Add a new movie to a user’s list of favorite movies."""

    pass

@app.route('users/<int:user_id>/movies/<int:movie_id>/update',
           methods=['POST'])
def modify_movie_title(user_id, movie_id):
    """Modify the title of a specific movie in a user’s list,
    without depending on OMDb for corrections."""
    pass

@app.route('users/<int:user_id>/movies/<int:movie_id>/delete',
           methods=['POST'])
def delete_movie(user_id, movie_id):
    """Remove a specific movie from a user’s favorite movie list."""
    pass


if __name__ == '__main__':
  with app.app_context():
    db.create_all()

  app.run()