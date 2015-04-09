from flask.ext.sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from config import zeromq_relay_uri
import zmq

db = SQLAlchemy()
limiter = Limiter(global_limits=["120 per minute"])

zmq_relay_socket = None
zeromq_context = None

if zeromq_relay_uri:
    zeromq_context = zmq.Context()
    zmq_relay_socket = zeromq_context.socket(zmq.PUSH)
    zmq_relay_socket.connect(zeromq_relay_uri)
