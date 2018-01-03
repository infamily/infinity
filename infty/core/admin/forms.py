from django import forms

from infty.core.models import Topic, Comment
from infty.users.models import CryptoKeypair


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
