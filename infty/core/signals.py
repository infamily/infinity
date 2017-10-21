from langsplit import splitter

def _topic_pre_save(sender, instance, *args, **kwargs):
    """ Create or preserve language tags for topic title, body. """
    instance.title = splitter.split(instance.title, markdown=True, title=True)
    instance.body = splitter.split(instance.body, markdown=True)

def _comment_pre_save(sender, instance, *args, **kwargs):
    """ Create or preserve language tags for comment text. """
    instance.text = splitter.split(instance.text, markdown=True)
