"""
    Module for development configurations
"""

import os

class DevConfig:
    def __init__(self):
        self.SQLALCHEMY_DATABASE_URI = os.getenv("DEVELOPMENT_DATABASE_URL")
        self.ENV = "development"
        self.DEBUG = True
        self.PORT = 3000
        self.HOST = '0.0.0.0'