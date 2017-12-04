from django import forms

from infty.core.models import Type, Instance, Topic, Comment
from infty.users.models import CryptoKeypair


class TypeForm(forms.ModelForm):

    class Meta:
        model = Type
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


class TopicForm(forms.ModelForm):

    type = forms.ChoiceField(
        choices=Topic.TOPIC_TYPES,
        initial=Topic.IDEA
    )

    blockchain = forms.ChoiceField(
        choices=CryptoKeypair.KEY_TYPES,
        initial=False
    )

    class Meta:
        model = Topic
        exclude = []


class CommentForm(forms.ModelForm):

    blockchain = forms.ChoiceField(
        choices=CryptoKeypair.KEY_TYPES,
        initial=False
    )

    class Meta:
        model = Comment
        exclude = []
