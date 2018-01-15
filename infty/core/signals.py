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

    if instance.body:

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

        lang = instance.languages[0] if instance.languages else 'en'

        # Create and Link Needs
        for need in needs:

            title = '.:{}:{}'.format(lang, need.get('name'))
            tool = [key for key in need.keys() if key not in ['name']][0]
            body = '.:{}\n```{}: {}```'.format(lang, tool, need.get(tool))

            if not Needs.filter(body=body).exists():

                topic = Topic.objects.create(
                    title=title,
                    body=body,
                    owner=instance.owner,
                    type=0
                )

                instance.parents.add(topic)

        # Remove needs that are not

        tool = lambda _: [key for key in _.keys() if key not in ['name']][0]


        for need in Needs:

            if not need.body in ['.:{}\n```{}: {}```'.format(lang, tool(_), _[tool(_)]) for _ in needs]:
                need.delete()
