import socketio
from .logger import logger
from .event_triggers import (
    on_message_handler,
    on_start_handler,
    on_connect_handler,

)


class ProxyNamespaceManager(socketio.AsyncNamespace):
    async def on_start(self, sid, data):
        await on_start_handler(sid, data)

    def on_connect(self, sid, environ):
        logger.info("Environment", environ)
        logger.info(f"Client {sid} connected")
        # return False
        on_connect_handler(socket_id=sid)

    async def on_message(self, sid, message_data):
        await on_message_handler(socket_id=sid, data=message_data)


    def on_test(self, sid, data):
        logger.info(f"data: {data}")
        print("Test", data)


    def on_disconnect(self, sid):
        logger.info(f"Client {sid} disconnected")
