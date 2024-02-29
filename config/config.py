from config.dev_config import DevConfig
from config.production_config import ProductionConfig

class Config:
    
    """
        Initialize Configurations
    """
    
    def __init__(self):
        self.dev_config = DevConfig()
        self.production_config = ProductionConfig()