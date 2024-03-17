from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config.config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    config = Config().dev_config
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    return app