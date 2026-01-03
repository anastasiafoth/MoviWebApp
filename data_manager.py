from models import db, User, Movie

class DataManager():
    def create_user(self, name):
        """Adds a new user to database"""
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()

    def get_users(self):
        """Returns a list of all users in database"""
        return User.query.all()

    def get_movies(self, user_id):
        """Returns a list of all movies of a specific user."""
        movies_based_on_user = (Movie.query.
                                filter(Movie.user_id==user_id).all())
        return movies_based_on_user

    def add_movie(self, movie):
        """Add a new movie to a user’s favorites."""
        db.session.add(movie)
        db.session.commit()

    def update_movie(self, movie_id, new_title):
        """Update the details of a specific movie in the database."""
        movie_to_update = Movie.query.get(movie_id)
        if not movie_to_update:
            return False

        movie_to_update.name = new_title
        db.session.commit()
        return True

    def delete_movie(self, movie_id):
        """Delete the movie from the user’s list of favorites."""
        movie_to_delete = Movie.query.get(movie_id)
        if not movie_to_delete:
            return False

        db.session.delete(movie_to_delete)
        db.session.commit()
        return True