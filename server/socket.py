# server/socket.py
import socketio
# Register the namespace
from .socket_manager import ProxyNamespaceManager


sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
)


sio.register_namespace(ProxyNamespaceManager("/"))

sio_asgi_app = socketio.ASGIApp(socketio_server=sio)
