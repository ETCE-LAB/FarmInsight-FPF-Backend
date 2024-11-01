from .base import *

# Disable debug mode in production
DEBUG = False

# Allowed hosts for production
ALLOWED_HOSTS = ['your-production-domain.com']

# Load production environment variables
environ.Env.read_env(os.path.join(BASE_DIR, '.env.prod'))

# Security settings for production
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/path/to/your/logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
