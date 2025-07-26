import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class AppConfig:
    # Application settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-here")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT settings
    JWT_SECRET = os.environ.get("JWT_SECRET", "your-jwt-secret-here")
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION = int(os.environ.get("JWT_EXPIRATION", 86400))  # 24 hours in seconds

    # OAuth settings
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    FACEBOOK_CLIENT_ID = os.environ.get("FACEBOOK_CLIENT_ID")
    FACEBOOK_CLIENT_SECRET = os.environ.get("FACEBOOK_CLIENT_SECRET")

    # Email settings
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "False").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

    # Web Scraping Configuration
    SCRAPING_ENABLED = os.environ.get("SCRAPING_ENABLED", "True").lower() == "true"
    SCRAPING_USER_AGENT = os.environ.get("SCRAPING_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    SCRAPING_DELAY_MIN = int(os.environ.get("SCRAPING_DELAY_MIN", 1))
    SCRAPING_DELAY_MAX = int(os.environ.get("SCRAPING_DELAY_MAX", 3))
    SCRAPING_TIMEOUT = int(os.environ.get("SCRAPING_TIMEOUT", 10))
    SCRAPING_MAX_RETRIES = int(os.environ.get("SCRAPING_MAX_RETRIES", 3))
    SCRAPING_BATCH_SIZE = int(os.environ.get("SCRAPING_BATCH_SIZE", 50))

    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # Chrome WebDriver Configuration
    CHROME_DRIVER_PATH = os.environ.get("CHROME_DRIVER_PATH", "chromedriver")
    CHROME_HEADLESS = os.environ.get("CHROME_HEADLESS", "True").lower() == "true"

    # Application URLs
    API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5000")
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

    # Environment
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

    # CORS settings
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
