import uuid
from django.db import models
from .action import Action
from .action_trigger import ActionTrigger


class ActionQueue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    startedAt = models.DateTimeField(null=True)
    endedAt = models.DateTimeField(null=True)
    value = models.TextField(null=True)
    action = models.ForeignKey(Action, related_name='queueEntries', on_delete=models.CASCADE)
    trigger = models.ForeignKey(ActionTrigger, on_delete=models.CASCADE)
