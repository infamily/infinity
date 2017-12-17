from django.db import models
from django.dispatch import receiver
from .models import Comment
from infty.api.v1.consumers import ws_send_comment_changed


@receiver(models.signals.post_save, sender=Comment)
def execute_after_save(sender, instance, created, *args, **kwargs):
    ws_send_comment_changed(instance, created)
