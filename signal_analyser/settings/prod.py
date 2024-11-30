import os
import dj_database_url
from .common import *

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ["signal-analyser-prod-3b21f0c9b70b.herokuapp.com"]

DATABASES = {
    "default": dj_database_url.config()
}
