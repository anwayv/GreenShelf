import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    UPI_ID = os.getenv("UPI_ID", "default@upi")
    HEADLESS = os.getenv("HEADLESS", "True") == "True"
    PINCODE = os.getenv("PINCODE", "")
    SELENIUM_TIMEOUT = int(os.getenv("SELENIUM_TIMEOUT", "15"))
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///green_shelf.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI Integration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCsbum8WsgutO43e50t8daKRPHvOP8CfLk")
    
    # File uploads
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Blinkit automation
    BLINKIT_BASE_URL = "https://www.blinkit.com"
    AUTOMATION_BACKEND_URL = os.getenv("AUTOMATION_BACKEND_URL", "")