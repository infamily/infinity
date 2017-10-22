from langsplit import splitter
from collections import OrderedDict

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
        instance.body = splitter.convert(body).strip()

    instance.languages = list(langs.keys())


def _comment_pre_save(sender, instance, *args, **kwargs):

    """ Create or preserve language tags for comment text. """
    text = splitter.split(instance.text)
    splitted = splitter.convert(text).strip()
    if splitted.startswith('\r\n'):
        instance.text = splitted[2:]
    instance.languages = list(text.keys())
