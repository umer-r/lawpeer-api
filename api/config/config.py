from api.config.dev_config import DevConfig
from api.config.production_config import ProductionConfig

class Config:
    
    """
        Initialize Configurations
    """
    
    def __init__(self):
        self.dev_config = DevConfig()
        self.production_config = ProductionConfig()