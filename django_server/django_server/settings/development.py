from .base import *
import colorlog

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
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(levelname)s: %(message)s',
            'log_colors': {
                'DEBUG': 'blue',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'fpf_sensor_service': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
