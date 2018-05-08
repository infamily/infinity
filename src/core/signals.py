import json

import boto3
import mistune
import bs4
import yaml
from django.conf import settings

from django.db import models
from django.dispatch import receiver

from src.core.models import Topic, Comment
from src.users.models import User
from src.websocket.consumers import ws_send_comment_changed

from src.mail import send_mail_async
from django.core.signing import Signer



@receiver(models.signals.post_save, sender=Comment)
def comment_post_save(sender, instance, created, *args, **kwargs):

    # Utils and constants
    signer = Signer()

    server = next(iter(settings.ALLOWED_HOSTS or []), None)
    if server == '*':
        server = '0.0.0.0:8000'

    client_server = server[4:] if server.startswith('.inf') else server

    # Broadcast over web-sockets
    ws_send_comment_changed(instance, created)

    # Send e-mail notification

    subscribers = {instance.topic.owner.pk}.union(set(
        Comment.objects.filter(
            topic=instance.topic).values_list(
                'owner_id', flat=True).distinct()))

    unsubscribed = {instance.owner.pk}.union(set(
        instance.topic.unsubscribed.all().values_list('pk', flat=True)))

    recipients = User.objects.filter(pk__in=subscribers-unsubscribed)

    subject = '{} - {}'.format(settings.EMAIL_SUBJECT_PREFIX, instance.topic.title[5:])

    for recipient in recipients:

        body = """Comment by {author}:<br>
<br>
{body}<br>
<br>
To reply, visit: https://{client}/#/{client_server}:{lang}/@/topic/{topic_id}/comment/{comment_id}<br>
<br>
--<br>
To unsubscribe from this topic, visit:<br>
https://{server}/unsubscribe/{topic_id}?sign={signed_email}<br>""".format(
        body=instance.text[5:],
        server=server,
        client=settings.CLIENT_DOMAIN,
        client_server=client_server,
        lang=instance.topic.title[2:4],
        topic_id=instance.topic.pk,
        comment_id=instance.pk,
        author=instance.owner.username,
        signed_email=signer.sign(recipient.email))

        send_mail_async(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [recipient.email],
            [settings.DEFAULT_FROM_EMAIL],
        )

    # Subscribe the commenter (instance.owner) to the (instance.topic):
    instance.topic.unsubscribed.remove(instance.owner)
    # (if previously was unsubscribed)


@receiver(models.signals.post_save, sender=Topic)
def topic_post_save(sender, instance, created, *args, **kwargs):

    if instance.body:

        html = mistune.markdown(instance.body)

        soup = bs4.BeautifulSoup(
            mistune.markdown(instance.body),
            'html.parser'
        )

        # Parse Needs

        targets = soup.find_all('code', {'class': 'lang-inf'})

        get_slice = lambda _, excluding: {
            key: _[key] for key in [key for key in _.keys() if key not in excluding]}

        needs = []

        for target in targets:
            for block in yaml.load(target.text):

                if 'needs' in block.keys():
                    items = block.get('needs')
                    if 'target' in block.keys():

                        for i, _ in enumerate(items):
                            items[i].update(
                                {'target': block['target']}
                            )
                            tools = get_slice(items[i], excluding=['name', 'target'])
                            items[i].update(
                                {'tool': tools}
                            )

                            for key, tool in enumerate(tools):
                                del items[i][tool]

                    needs.extend(items)


        lang = instance.languages[0] if instance.languages else 'en'

        # Update Needs

        for need in needs:

            title='.:{}:{}'.format(lang, need['name'])
            body = '.:{}\n```\n{}\n```'.format(lang, yaml.dump(need, default_flow_style=False, allow_unicode=True))

            if not instance.parents.filter(title=title).exists():
                topic = Topic.objects.create(
                    title=title,
                    body=body,
                    owner=instance.owner,
                    type=0
                )
                instance.parents.add(topic)
                instance.save()
            else:

                topic = instance.parents.filter(title=title).first()
                topic.body = body
                topic.save()

        for need in instance.parents.filter(type=0):
            if need.title not in ['.:{}:{}'.format(lang, d['name']) for d in needs]:
                need.delete()


@receiver(models.signals.post_save, sender=Topic)
def send_sns_notification(sender, instance, created, *args, **kwargs):
    if not created:
        return

    arn = getattr(settings, 'TOPIC_CREATED_ARN')
    if not arn:
        return

    region = getattr(settings, 'AWS_DEFAULT_REGION')
    if not region:
        return

    client = boto3.client('sns', region_name=region)
    message = {"topic_id": instance.pk}
    client.publish(
        TopicArn=arn,
        Message=json.dumps(message)
    )
