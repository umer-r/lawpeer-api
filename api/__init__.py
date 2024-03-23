from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Import Routes
from api.routes.users.urls import user_routes

# Import Modules
from api.database import db
from api.config.config import Config

load_dotenv()  # Load environment variables from .env

# Flask app configs
def create_app():  
    app = Flask(__name__)
    config = Config().dev_config
    app.config.from_object(config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    cors_origin = os.environ.get('ALLOWED_ORIGIN')
    CORS(app)

    # Db init - 1
    migrate = Migrate()
    db.init_app(app)
    migrate.init_app(app, db)

    # Register routes
    app.register_blueprint(user_routes, url_prefix='/api/users')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()