from flask import Blueprint, current_app, jsonify, request
import google.auth
from flask_jwt_extended import get_jwt_identity, jwt_required
from langchain.llms import VertexAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
import requests

# Get your google cloud credentials. Set up with Gcloud if needed
credentials, project_id = google.auth.default()


nutrition_bp = Blueprint('nutrition_bp', __name__)


