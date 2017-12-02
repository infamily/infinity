from django.db import models


class GenericManager(models.Manager):
    pass


class GenericModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = GenericManager()

    class Meta:
        abstract = True


class GenericSnapshot(GenericModel):
    blockchain = models.PositiveSmallIntegerField(blank=True, null=True)
    blockchain_tx = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True
