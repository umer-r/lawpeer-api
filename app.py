from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Import Routes
from routes.users.urls import user_routes

# Import Modules
from __init__ import create_app
from config.config import Config

load_dotenv()  # Load environment variables from .env

app = create_app()

cors_origin = os.environ.get('ALLOWED_ORIGIN')
CORS(app)

# Load configuration based on environment
config = Config().dev_config
app.config.from_object(config)

# Register routes
app.register_blueprint(user_routes, url_prefix='/api/users')

app.route('/api', methods=['GET'])
def index():
    return {'message': 'Welcome to lawpeer-api'}

if __name__ == '__main__':
    app.run()