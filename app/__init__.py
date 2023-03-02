from flask import Flask
from flask_migrate import Migrate, upgrade

from app.auth.routes import auth_bp, login_manager
from app.routes import main_bp
from backend.database import db
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config.from_object(config_class)
    db.init_app(app)

    from app.auth.models import User
    from app.models import Channel

    app.register_blueprint(auth_bp, login_manager=login_manager)
    app.register_blueprint(main_bp)
    login_manager.init_app(app)

    migrate = Migrate(app, db)
    with app.app_context():
        migrate.init_app(app, db)
        upgrade()

        # create the db and table
        db.create_all()

    return app
