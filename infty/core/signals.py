import mistune
import bs4
import yaml

from django.db import models
from django.dispatch import receiver

from infty.core.models import Topic, Comment
from infty.api_asgi.consumers import ws_send_comment_changed


@receiver(models.signals.post_save, sender=Comment)
def execute_after_save(sender, instance, created, *args, **kwargs):
    ws_send_comment_changed(instance, created)

@receiver(models.signals.post_save, sender=Topic)
def topic_post_save(sender, instance, created, *args, **kwargs):

    html = mistune.markdown(instance.body)

    # Parse Needs
    soup = bs4.BeautifulSoup(
        mistune.markdown(instance.body),
        'html.parser'
    )

    need_lists = soup.find_all(
        'code', {'class': 'lang-yml'}
    )

    needs = []
    for need_list in need_lists:
        blocks = yaml.load(need_list.text)
        for block in blocks:
            if 'needs' in block.keys():
                needs.extend(block['needs'])

    # Retrieve Existing Needs:
    Needs = instance.parents.filter(type=0)

    # Create and Link Needs
    for need in needs:

        lang = 'en'
        title = '.:{}:{}'.format(lang, need.get('name'))
        body = '.:{}\n{}'.format(lang, need.get('vals'))

        if not Needs.filter(body=body).exists():

            topic = Topic.objects.create(
                title=title,
                body=body,
                owner=instance.owner,
                type=0
            )

            instance.parents.add(topic)
