from django import forms

from infty.core.models import Topic

class TopicForm(forms.ModelForm):

    type = forms.ChoiceField(
        choices=Topic.TOPIC_TYPES,
        initial=Topic.IDEA
    )

    class Meta:
        model = Topic
        exclude = []
