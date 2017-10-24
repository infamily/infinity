from django import forms

from infty.core.models import Item, Topic


class ItemForm(forms.ModelForm):

    type = forms.ChoiceField(
        choices=Item.ITEM_TYPES,
        initial=Item.AGENT
    )

    class Meta:
        model = Item
        exclude = []


class TopicForm(forms.ModelForm):

    type = forms.ChoiceField(
        choices=Topic.TOPIC_TYPES,
        initial=Topic.IDEA
    )

    class Meta:
        model = Topic
        exclude = []
