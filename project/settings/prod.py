from .base import *

DEBUG = False

ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", "").split(",")
