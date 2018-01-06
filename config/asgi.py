"""
ASGI entrypoint file for default channel layer.

Points to the channel layer configured as "default" so you can point
ASGI applications at "config.asgi:channel_layer" as their channel layer.
"""
from channels.asgi import get_channel_layer

channel_layer = get_channel_layer()

