from .common import *

DEBUG = True

ALLOWED_HOSTS = ['10.249.53.47']

SECRET_KEY = "django-insecure-*ak%y3zg-z^qq^%rk@zgtqg2q)#2+hz^4tn1(tvske)xcq3b$n"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": 'signal_analyser',
        "HOST": 'localhost',
        "USER": 'root',
        "PASSWORD": ''
    }
}

