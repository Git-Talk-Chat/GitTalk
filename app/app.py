import os
from flask import Flask
from dotenv import load_dotenv
from supabase import create_client, Client
from config import Config

load_dotenv()

app = Flask(__name__)

app.config.from_object(Config)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)


url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

from routes.common import common_bp
from routes.auth import auth_bp

app.register_blueprint(common_bp)
app.register_blueprint(auth_bp)