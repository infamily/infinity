import json
from channels import Group
from channels.auth import channel_session

from django.forms.models import model_to_dict
from django.core import serializers

from infty.api.v1.serializers import CommentSerializer


def get_general_label():
    return 'comments'


def get_label(group_id):
    return 'comments-%s' % group_id


@channel_session
def ws_connect(message):
    path_items = message['path'].strip('/').split('/')

    if path_items[0] != 'comments':
        return

    if len(path_items) > 1:
        channel_id = path_items[1]
        label= get_label(channel_id)
    else:
        label = get_general_label()

    Group(label).add(message.reply_channel)
    message.channel_session['channnel_label'] = label

    # Accept connection
    message.reply_channel.send({"accept": True})


def ws_send_comment_changed(comment, created):
    data = serializers.serialize('json', [ comment, ])
    message =  {
        'text': json.dumps(data)
    }

    Group(get_general_label()).send(message)
    Group(get_label(comment.topic.id)).send(message)


@channel_session
def ws_disconnect(message):
    label = message.channel_session['channnel_label']
    Group(label).discard(message.reply_channel)
