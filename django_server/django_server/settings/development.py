from .base import *

# Enable debug mode for development
DEBUG = True

# Allowed hosts for development
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Development-specific environment variables
environ.Env.read_env(os.path.join(BASE_DIR, '.env.dev'))
MEASUREMENTS_BASE_URL = env('MEASUREMENTS_BASE_URL')

# For logging in the console
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
