import json
from channels import Group
from channels.auth import channel_session
from django.forms.models import model_to_dict
from django.core import serializers


@channel_session
def ws_connect(message):
    label = '-'.join(message['path'].strip('/').split('/'))

    Group(label).add(message.reply_channel)
    message.channel_session['channel_label'] = label

    # Accept connection
    message.reply_channel.send({"accept": True})


def ws_send_comment_changed(comment, created):
    obj = serializers.serialize('json', [ comment, ])
    message =  {
        'text': json.dumps({
            'comment': obj,
            'created': created,
        })
    }

    Group('comments').send(message)
    Group('comments-' + str(comment.topic.id)).send(message)


@channel_session
def ws_disconnect(message):
    label = message.channel_session['channel_label']
    Group(label).discard(message.reply_channel)
