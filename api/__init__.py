"""
    DESC: 
        Initializer module for creating and configuring the Flask application.

    Module Imports:
        - user_routes: Blueprint for user-related routes.
        - admin_routes: Blueprint for admin-related routes.
        - create_super_admin: Function for creating a super admin during application initialization.
        - db: Database instance for SQLAlchemy.
        - Config: Class for loading configuration settings.

    Library Imports:
        - Flask: Web framework for building the application.
        - Migrate: Extension for handling database migrations.
        - CORS: Cross-Origin Resource Sharing middleware for handling CORS.
        - load_dotenv: Function for loading environment variables from a .env file.
        - JWTManager: Extension for handling JWT authentication.
        - os: Operating system module for interacting with the operating system.
        - socketio: Socket.IO library for real-time communication.
        - flasgger: Api documentation library provided by swagger.
        - stripe: A payment integration gateway.


    Functions:
        - create_app(): 
            Creates and configures the Flask application.
"""

# Lib Imports:
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flasgger import Swagger
import stripe
import os

# Import Routes:
from api.routes.users.urls import user_routes
from api.routes.admin.urls import admin_routes
from api.routes.chats.urls import chat_routes
from api.routes.contracts.urls import contract_routes
from api.routes.complaints.urls import complaint_routes

# Initialize admin:
from api.routes.admin.controllers import create_super_admin

# Import Modules:
from api.database import db
from api.config.config import Config
from api.socketio import init_app as init_socketio

# ----------------------------------------------- #

# Load environment variables from .env:
load_dotenv()  

def create_app():  
    """
    Creates and configures the Flask application.

    Returns:
        Flask: The configured Flask application.
    """
    
    app = Flask(
            __name__,
            static_url_path='/static', 
            static_folder='assets/uploaded',
        )

    config = Config().dev_config
    app.config.from_object(config)
    jwt = JWTManager(app)
    
    cors_origin = os.environ.get('ALLOWED_ORIGIN')
    CORS(app)

    # Initialize SocketIO
    init_socketio(app)
    
    # Initialize Swagger
    swagger = Swagger(app)

    # Db init:
    migrate = Migrate()
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Stripe:
    stripe.api_key = app.config['STRIPE_SEC_KEY']

    # Call create_super_admin within application context
    with app.app_context():
        create_super_admin()

    # Register routes:
    app.register_blueprint(user_routes, url_prefix='/api/users')
    app.register_blueprint(admin_routes, url_prefix='/api/admin')
    app.register_blueprint(chat_routes, url_prefix='/api/chat')
    app.register_blueprint(contract_routes, url_prefix='/api/contract')
    app.register_blueprint(complaint_routes, url_prefix='/api/complaint')
    
    print(app.url_map)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
