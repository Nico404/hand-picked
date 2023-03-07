from flask_login import LoginManager, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from backend.database import db

login_manager = LoginManager()

# UserMixin is a class that provides default implementations for the methods that Flask-Login expects user objects to have. ie is_active here.
class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email_confirmed = db.Column(db.Boolean, default=False)
    youtube_credentials = db.Column(db.String(500), nullable=True)

    def update_youtube_credentials(self, credentials):
        self.youtube_credentials = credentials.to_json()
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # this is required by flask_login because id of user is user_id not id by default
    def get_id(self):
        return self.user_id

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
