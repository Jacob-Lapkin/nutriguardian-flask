
class Config:
    VERSION = 'v1'
    SECRET_KEY = "ashjkasdkbj3"
    
class Development(Config):
    MONGO_URI = "mongodb://localhost:27017"
    SQUARE_ACCESS_TOKEN = "YOUR_DEVELOPMENT_SQUARE_ACCESS_TOKEN"
    
class Production(Config):
    MONGO_URI = "YOUR_PRODUCTION_MONGO_URI"
    SQUARE_ACCESS_TOKEN = "YOUR_PRODUCTION_SQUARE_ACCESS_TOKEN"