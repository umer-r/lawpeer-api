"""
    Module for production configurations
"""

import os

class ProductionConfig:
    def __init__(self):
        self.SQLALCHEMY_DATABASE_URI = os.getenv("PRODUCTION_DATABASE_URL")
        self.ENV = "production"
        self.DEBUG = False
        self.PORT = 80
        self.HOST = '0.0.0.0'