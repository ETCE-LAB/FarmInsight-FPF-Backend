from enum import Enum

from django.db import models


class ConfigurationKeys(Enum):
    FPF_ID = 'fpfId'
    API_KEY = 'apiKey'


class Configuration(models.Model):
    key = models.CharField(max_length=100, unique=True, blank=False, null=False)
    value = models.CharField(max_length=1024, blank=False, null=False)