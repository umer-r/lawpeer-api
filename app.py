from flask import Flask
from flask_cors import CORS
from config.config import Config
from dotenv import load_dotenv
import os

# Import Routes
from routes.users_routes import user_routes

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
cors_origin = os.environ.get('ALLOWED_ORIGIN')
CORS(app)

# Load configuration based on environment
config = Config().production_config

app.config.from_object(config)

# Register routes
app.register_blueprint(user_routes, url_prefix='/api/users')

app.route('/api', methods=['GET'])
def index():
    return {'message': 'Welcome to dewdevine-api'}

if __name__ == '__main__':
    app.run()