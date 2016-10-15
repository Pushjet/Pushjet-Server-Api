from flask import Blueprint, jsonify, request
from flask import current_app

from utils import Error, has_uuid, has_secret, queue_zmq_message
from shared import db
from models import Subscription, Message, Gcm
from datetime import datetime
from config import zeromq_relay_uri, google_api_key
from json import dumps as json_encode

message = Blueprint('message', __name__)


@message.route('/message', methods=['POST'])
@has_secret
def message_send(service):
    text = request.form.get('message')
    if not text:
        return Error.ARGUMENT_MISSING('message')

    subscribers = Subscription.query.filter_by(service=service).count()
    if subscribers == 0:
        # Pretend we did something even though we didn't
        # Nobody is listening so it doesn't really matter
        return Error.NONE

    level = (request.form.get('level') or '3')[0]
    level = int(level) if level in "12345" else 3
    title = request.form.get('title', '').strip()[:255]
    link = request.form.get('link', '').strip()
    msg = Message(service, text, title, level, link)
    db.session.add(msg)
    db.session.commit()

    if google_api_key or current_app.config['TESTING']:
        Gcm.send_message(msg)

    if zeromq_relay_uri:
        queue_zmq_message(json_encode({"message": msg.as_dict()}))

    service.cleanup()
    db.session.commit()
    return Error.NONE


@message.route('/message', methods=['GET'])
@has_uuid
def message_recv(client):
    subscriptions = Subscription.query.filter_by(device=client).all()
    if len(subscriptions) == 0:
        return jsonify({'messages': []})

    msg = []
    for l in subscriptions:
        msg += l.messages().all()

    last_read = max([0] + [m.id for m in msg])
    for l in subscriptions:
        l.timestamp_checked = datetime.utcnow()
        l.last_read = max(l.last_read, last_read)
        l.service.cleanup()

    ret = jsonify({'messages': [m.as_dict() for m in msg]})
    db.session.commit()
    return ret


@message.route('/message', methods=['DELETE'])
@has_uuid
def message_read(client):
    subscriptions = Subscription.query.filter_by(device=client).all()
    if len(subscriptions) > 0:
        last_message = Message.query.order_by(Message.id.desc()).first()
        for l in subscriptions:
            l.timestamp_checked = datetime.utcnow()
            l.last_read = last_message.id if last_message else 0

        for l in subscriptions:
            l.service.cleanup()
        db.session.commit()

    return Error.NONE
