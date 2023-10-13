
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

square_access_token = os.getenv("SQUARE_ACCESS_TOKEN")

class Config:
    VERSION = 'v1'
    SECRET_KEY = "ashjkasdkbj3"
    JWT_SECRET_KEY="asdfasdas"
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1)
    
class Development(Config):
    MONGO_URI = "mongodb://localhost:27017"
    SQUARE_ACCESS_TOKEN = square_access_token
    DEBUG=True

class Production(Config):
    MONGO_URI = "YOUR_PRODUCTION_MONGO_URI"
    SQUARE_ACCESS_TOKEN = square_access_token
    DEBUG=False