from flask import Blueprint, jsonify
from utils import Error, has_service, has_uuid, queue_zmq_message, QUERY_UPDATE_LISTEN
from shared import db
from models import Listen
from json import dumps as json_encode
from config import zeromq_relay_uri

listen = Blueprint('listen', __name__)


@listen.route('/listen', methods=['POST'])
@has_uuid
@has_service
def listen_post(client, service):
    exists = Listen.query.filter_by(device=client).filter_by(service=service).first() is not None
    if exists:
        return jsonify(Error.DUPLICATE_LISTEN)

    listen_new = Listen(client, service)
    db.session.add(listen_new)
    db.session.commit()

    if zeromq_relay_uri:
        queue_zmq_message(json_encode({'listen': listen_new.as_dict()}))

    return jsonify({'service': service.as_dict()})


@listen.route('/listen', methods=['GET'])
@has_uuid
def listen_get(client):
    listens = Listen.query.filter_by(device=client).all()
    return jsonify({'listen': [_.as_dict() for _ in listens]})


@listen.route('/listen', methods=['DELETE'])
@has_uuid
@has_service
def listen_delete(client, service):
    l = Listen.query.filter_by(device=client).filter_by(service=service).first()
    if l is not None:
        db.session.delete(l)
        db.session.commit()
    return jsonify(Error.NONE)
