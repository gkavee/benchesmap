import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PASS = os.environ.get("DB_PASS")
DB_USER = os.environ.get("DB_USER")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = os.environ.get("DB_PORT")

DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
DB_PASS_TEST = os.environ.get("DB_PASS_TEST")
DB_USER_TEST = os.environ.get("DB_USER_TEST")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DB_PORT_TEST = os.environ.get("DB_PORT_TEST")

SECRET = os.environ.get("SECRET")
SECRET_PASS = os.environ.get("SECRET_PASS")
SECRET_VER = os.environ.get("SECRET_VER")

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
