from django import forms

from infty.core.models import Item, Type, Topic, Comment
from infty.users.models import CryptoKeypair


class ItemForm(forms.ModelForm):

    role = forms.ChoiceField(
        choices=Item.ITEM_ROLES,
        initial=Item.ASSET
    )

    identifiers = forms.CharField()

    class Meta:
        model = Item
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
