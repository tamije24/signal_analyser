from .common import *

DEBUG = False

ALLOWED_HOSTS = ['*']

ALLOWED_HOSTS = ['10.250.53.47']

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