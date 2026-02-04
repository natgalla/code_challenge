from flask import Flask

from config import Config
from app.extensions import db, login_manager
from app.models import User, Starship
from app.services import fetch_starship_data


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes import bp
    app.register_blueprint(bp)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Create tables and seed data
    with app.app_context():
        db.create_all()
        starship_count = db.session.execute(db.select(db.func.count()).select_from(Starship)).scalar()
        if starship_count == 0:
            print('No starships in DB, fetching from SWAPI...')
            fetch_starship_data()

    return app
