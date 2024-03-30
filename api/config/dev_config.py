"""
    Module for development configurations
"""

import os

class DevConfig:
    def __init__(self):
        self.SQLALCHEMY_DATABASE_URI = os.getenv("DEVELOPMENT_DATABASE_URL")
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET")
        self.JWT_ACCESS_TOKEN_EXPIRES = 604800
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.ENV = "development"
        self.DEBUG = True
        self.PORT = 3000
        self.HOST = '0.0.0.0'