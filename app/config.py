import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "secret_conquia_secret")
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
