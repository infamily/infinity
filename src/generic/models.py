from langsplit import splitter

from django.db import models
from django.contrib.postgres.fields import ArrayField
import django.db.models.options as options

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('translation_fields',)


class GenericManager(models.Manager):
    pass


class GenericModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = GenericManager()

    class Meta:
        abstract = True


class GenericTranslationModel(GenericModel):
    languages = ArrayField(models.CharField(max_length=2), blank=True)

    def save(self, *args, **kwargs):
        translation_fields = getattr(self._meta, 'translation_fields', ())
        lang_keys = []
        for translation_field, translation_title in translation_fields:
            try:
                field_data = splitter.split(
                    getattr(self, translation_field),
                    title=translation_title
                )
                if field_data:
                    setattr(
                        self,
                        translation_field,
                        splitter.convert(
                            field_data,
                            title=translation_title
                        ).strip()
                    )
                    lang_keys.append(field_data.keys())
            except Exception:
                pass

        # TODO ordering issue
        self.languages = list(
            frozenset.intersection(
                *[frozenset(key_pair) for key_pair in lang_keys]
            )
        )
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
