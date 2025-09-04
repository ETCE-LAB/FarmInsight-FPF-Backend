import os

import environ
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env.dev'))

SECRET_KEY = env('SECRET_KEY', default='your-default-secret-key')

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'fpf_sensor_service',
    'oauth2_provider',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

'''
We're using Daphne to host the FPF server, because of that it is an asgi application and can still be
started using runserver as daphne is supposed to be production ready.
'''
ASGI_APPLICATION = 'django_server.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

SERVER_PORT = env('SERVER_PORT', default=8001)

DEBUG = env('DEBUG', default='True') == 'True'

MEASUREMENTS_BASE_URL = env('MEASUREMENTS_BASE_URL')
GENERATE_MEASUREMENTS = env('GENERATE_MEASUREMENTS', default='False') == 'True'
MEASUREMENT_PACKAGE_SIZE = env('MEASUREMENT_PACKAGE_SIZE', default=50)
MEASUREMENT_RETRY_COUNT = env('MEASUREMENT_RETRY_COUNT', default=3)
MEASUREMENT_RETRY_SLEEP_BETWEEN_S = env('MEASUREMENT_RETRY_SLEEP_BETWEEN_S', default=5)

USE_DEFAULT_IMAGE = env('USE_DEFAULT_IMAGE', default='False') == 'True'
DEFAULT_IMAGE_PATH = env('DEFAULT_IMAGE_PATH', default=os.path.join(BASE_DIR, 'test.jpg'))

'''
DASHBOARD_BACKEND_USER_ID and RESOURCE_SERVER_INTROSPECTION_URL are intended to be used with an external identity server
to ensure only a known dashboard backend can send configurations to the FPF.
Since we currently don't have the external identity server, because of that at the moment we only check for the existence of the 
mock token in the "custom_oauth_validator.py" this is insecure while this is on github, it would be better to move this token
to an env for the FPF and the Dashboard backend in the future.s 
'''
# DASHBOARD_BACKEND_USER_ID = env('DASHBOARD_BACKEND_USER_ID')

OAUTH2_PROVIDER = {
    'SCOPES': {"openid": ''},
    'RESOURCE_SERVER_INTROSPECTION_URL': env('RESOURCE_SERVER_INTROSPECTION_URL', default='https://development-isse-identityserver.azurewebsites.net/connect/introspect'),
    'RESOURCE_SERVER_INTROSPECTION_CREDENTIALS': ('interactive', ''),
    'OAUTH2_VALIDATOR_CLASS': 'fpf_sensor_service.custom_oauth_validator.CustomOAuth2Validator',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ),
}

MQTT_CONFIG = {
    "HOST": env("MQTT_HOST", default="localhost"),
    "PORT": env.int("MQTT_PORT", default=1883),
    "USERNAME": env("MQTT_USERNAME", default=None),
    "PASSWORD": env("MQTT_PASSWORD", default=None),
}

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
        'plain': {  # Add a new plain formatter for the file handler
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        'message_only': {
            'format': '%(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'django_server.custom_loggers.CustomConsoleLogger', # handles our extra information like sensorId
            'formatter': 'colored',
            'level': 'DEBUG',
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'plain',
            'level': 'DEBUG',
            'filename': 'myapp.log',
        },
        'api': {
            'level': env('API_LOG_LEVEL', default='ERROR'),
            'class': 'django_server.custom_loggers.APILogHandler',
            'api_url': f'{MEASUREMENTS_BASE_URL}/api/log_messages',
            'fpf_id': '',
            'formatter': 'message_only',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'fpf_sensor_service': {
            'handlers': ['console', 'api'],
            'level': env('SENSOR_SERVICE_LOG_LEVEL', default='DEBUG'),
            'propagate': False,
        },
    },
}
