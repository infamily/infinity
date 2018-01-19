from django import forms

from src.meta.models import Type, Schema, Instance


class TypeForm(forms.ModelForm):

    class Meta:
        model = Type
        exclude = []


class SchemaForm(forms.ModelForm):

    class Meta:
        model = Schema
        exclude = []


class InstanceForm(forms.ModelForm):

    role = forms.ChoiceField(
        choices=Instance.ITEM_ROLES,
        initial=Instance.THING
    )

    identifiers = forms.CharField()

    class Meta:
        model = Instance
        exclude = []
