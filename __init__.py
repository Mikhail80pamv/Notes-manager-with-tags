from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'  # обновили для Blueprint
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # Импорт Blueprint и моделей
    from app.routes import main
    app.register_blueprint(main)

    from app import models

    with app.app_context():
        db.create_all()

    return app