from decouple import config 
environment = config('ENV') or None

if environment == 'prod':
    from .prod import *
elif environment == 'dev':
    from .dev import *
else:
    raise KeyError('Please create an environment variable .env file in the root directory and specify the keyword "ENV" & its value to anyone of the following "prod/dev".')