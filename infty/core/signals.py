from langsplit import splitter
from collections import OrderedDict

def _type_pre_save(sender, instance, *args, **kwargs):

    """ Create or preserve language tags for Type definition. """

    name = splitter.split(instance.name, title=True)
    try:
        definition = splitter.split(instance.definition)
    except Exception as e:
        print(e)
        definition = None

    langs = OrderedDict()
    for lang in list(name.keys()) + list(definition.keys()) if definition else []:
        if lang in name.keys() and lang in definition.keys():
            langs[lang] = True

    instance.name = splitter.convert(name, title=True).strip()

    if definition:
        instance.definition = splitter.convert(definition)

    instance.languages = list(langs.keys())

def _item_pre_save(sender, instance, *args, **kwargs):

    """ Create or preserve language tags for Item text. """
    description = splitter.split(instance.description)

    instance.description = splitter.convert(description)

    if isinstance(description, dict):
        instance.languages = list(description.keys())
    else:
        instance.languages = []

def _topic_pre_save(sender, instance, *args, **kwargs):

    """ Create or preserve language tags for topic title, body. """
    title = splitter.split(instance.title, title=True)
    try:
        body = splitter.split(instance.body)
    except Exception as e:
        print(e)
        body = None

    langs = OrderedDict()
    for lang in list(title.keys()) + list(body.keys()) if body else []:
        if lang in title.keys() and lang in body.keys():
            langs[lang] = True

    instance.title = splitter.convert(title, title=True).strip()

    if body:
        instance.body = splitter.convert(body)

    instance.languages = list(langs.keys())

def _topic_post_save(sender, instance, created, *args, **kwargs):
    """
    Create topic snapshot in blockchain, if requested.
    """
    if instance.blockchain:
        instance.create_snapshot(blockchain=instance.blockchain)

def _comment_pre_save(sender, instance, *args, **kwargs):

    """ Create or preserve language tags for comment text. """
    text = splitter.split(instance.text)

    instance.text = splitter.convert(text)

    if isinstance(text, dict):
        instance.languages = list(text.keys())
    else:
        instance.languages = []

def _comment_post_save(sender, instance, created, *args, **kwargs):
    """
    Create comment snapshot in blockchain, if requested.
    """
    if instance.blockchain:
        instance.create_snapshot(blockchain=instance.blockchain)
