from flask import Blueprint, jsonify
from utils import Error, has_service, has_uuid, queue_zmq_message
from shared import db
from models import Subscription
from json import dumps as json_encode
from config import zeromq_relay_uri

subscription = Blueprint('subscription', __name__)


@subscription.route('/subscription', methods=['POST'])
@has_uuid
@has_service
def subscription_post(client, service):
    exists = Subscription.query.filter_by(device=client).filter_by(service=service).first() is not None
    if exists:
        return Error.DUPLICATE_LISTEN

    subscription_new = Subscription(client, service)
    db.session.add(subscription_new)
    db.session.commit()

    if zeromq_relay_uri:
        queue_zmq_message(json_encode({'subscription': subscription_new.as_dict()}))

    return jsonify({'service': service.as_dict()})


@subscription.route('/subscription', methods=['GET'])
@has_uuid
def subscription_get(client):
    subscriptions = Subscription.query.filter_by(device=client).all()
    return jsonify({'subscriptions': [_.as_dict() for _ in subscriptions]})


@subscription.route('/subscription', methods=['DELETE'])
@has_uuid
@has_service
def subscription_delete(client, service):
    l = Subscription.query.filter_by(device=client).filter_by(service=service).first()
    if l is not None:
        db.session.delete(l)
        db.session.commit()
        return Error.NONE
    return Error.NOT_SUBSCRIBED
