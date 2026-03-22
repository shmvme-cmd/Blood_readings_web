import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///medical_analyses.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOOTSTRAP_SERVE_LOCAL = True
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')