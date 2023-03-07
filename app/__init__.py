from flask import Flask
from flask.cli import FlaskGroup
from flask_migrate import Migrate, upgrade

from app.auth.routes import auth_bp, login_manager
from app.routes import main_bp
from backend.database import db
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate = Migrate(app, db)

    app.register_blueprint(auth_bp, login_manager=login_manager)
    app.register_blueprint(main_bp)
    login_manager.init_app(app)

    @app.cli.command("create_database")
    def create_database():
        with app.app_context():
            db.create_all()

    return app


app = create_app()
cli = FlaskGroup(create_app=create_app)

if __name__ == "__main__":
    cli()
