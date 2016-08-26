from flask_sqlalchemy import SQLAlchemy
from config import zeromq_relay_uri
import zmq

db = SQLAlchemy()

zmq_relay_socket = None
zeromq_context = None

if zeromq_relay_uri:
    zeromq_context = zmq.Context()
    zmq_relay_socket = zeromq_context.socket(zmq.PUSH)
    zmq_relay_socket.connect(zeromq_relay_uri)
