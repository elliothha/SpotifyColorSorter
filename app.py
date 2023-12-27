import os

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['CLIENT_ID'] = os.getenv('CLIENT_ID')
    app.config['CLIENT_SECRET'] = os.getenv('CLIENT_SECRET')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='localhost', port=8888)