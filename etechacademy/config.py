import os

import dotenv

ok = dotenv.load_dotenv()
if not ok:
    raise ValueError("No .env file found for Flask application")

site_name = os.getenv("SITE_NAME")
if site_name is None:
    raise ValueError("No SITE_NAME set for Flask application")

web_app_port = os.getenv("WEB_APP_PORT")
if web_app_port is None:
    raise ValueError("No WEB_APP_PORT set for Flask application")

web_app_host = os.getenv("WEB_APP_HOST")
if web_app_host is None:
    raise ValueError("No WEB_APP_HOST set for Flask application")

db_host = os.getenv("POSTGRES_HOST")
if db_host is None:
    raise ValueError("No POSTGRES_HOST set for Flask application")

db_port = os.getenv("POSTGRES_PORT")
if db_port is None:
    raise ValueError("No POSTGRES_PORT set for Flask application")

db_user = os.getenv("POSTGRES_USER")
if db_user is None:
    raise ValueError("No POSTGRES_USER set for Flask application")

db_password = os.getenv("POSTGRES_PASSWORD")
if db_password is None:
    raise ValueError("No POSTGRES_PASSWORD set for Flask application")

db_name = os.getenv("POSTGRES_DB")
if db_name is None:
    raise ValueError("No POSTGRES_DB for Flask application")
