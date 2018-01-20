import mistune
import bs4
import yaml

from django.db import models
from django.dispatch import receiver

from src.core.models import Topic, Comment
from src.api_asgi.consumers import ws_send_comment_changed


@receiver(models.signals.post_save, sender=Comment)
def execute_after_save(sender, instance, created, *args, **kwargs):
    ws_send_comment_changed(instance, created)

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
