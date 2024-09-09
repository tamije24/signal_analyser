import os
import dj_database_url
from .common import *

DEBUG = True

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ["signal-analyser-prod-f706849603dd.herokuapp.com"]

DATABASES = {
    "default": dj_database_url.config()
}
