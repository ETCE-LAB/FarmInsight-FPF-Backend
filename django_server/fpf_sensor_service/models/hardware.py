import uuid
from django.db import models
from django.db.models import Max


def get_order_index_default():
    if Hardware.objects.all().count() == 0:
        new_order_default = 0
    else:
        new_order_default = Hardware.objects.all().aggregate(Max('orderIndex'))['orderIndex__max'] + 1
    return new_order_default


class Hardware(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    orderIndex = models.IntegerField(default=get_order_index_default)

    class Meta:
        ordering = ['orderIndex']
