
import os

from flask import Flask
from dotenv import load_dotenv

REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-read-private playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public'

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['CLIENT_ID'] = os.getenv('CLIENT_ID')
    app.config['CLIENT_SECRET'] = os.getenv('CLIENT_SECRET')

    from app.routes.auth import auth_bp
    from app.routes.sorting import sorting_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(sorting_bp)

    return app