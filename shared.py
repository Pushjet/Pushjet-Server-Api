from flask.ext.sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_sockets import Sockets
from config import zeromq_relay_uri, zeromq_subscriber_uri
import zmq

db = SQLAlchemy()
limiter = Limiter(global_limits=["120 per minute"])
sockets = Sockets()

zmq_relay_socket = None
zeromq_context = None

if zeromq_relay_uri or zeromq_subscriber_uri:
    zeromq_context = zmq.Context()

if zeromq_relay_uri:
    # ZMQ_PUSH == 8
    # See https://github.com/zeromq/libzmq/blob/862cd41c6521b988153eb7caafd07a5cd3ae8ba7/include/zmq.h#L237
    zmq_relay_socket = zeromq_context.socket(8)
    zmq_relay_socket.connect(zeromq_relay_uri)
