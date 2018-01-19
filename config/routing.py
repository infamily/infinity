from channels.routing import route
from src.api_asgi.consumers import (
    ws_connect,
    ws_disconnect
)


channel_routing = [
    route('websocket.connect', ws_connect),
    route('websocket.disconnect', ws_disconnect),
]
