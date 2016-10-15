from flask import Blueprint, jsonify, request
from utils import Error, is_service, is_secret, has_secret, queue_zmq_message
from models import Service, Message
from shared import db
from json import dumps as json_encode
from config import zeromq_relay_uri

service = Blueprint('service', __name__)


@service.route('/service', methods=['POST'])
def service_create():
    name = request.form.get('name', '').strip()
    icon = request.form.get('icon', '').strip()
    if not name:
        return Error.ARGUMENT_MISSING('name')
    srv = Service(name, icon)
    db.session.add(srv)
    db.session.commit()
    return jsonify({"service": srv.as_dict(True)})


@service.route('/service', methods=['GET'])
def service_info():
    secret = request.form.get('secret', '') or request.args.get('secret', '')
    service_ = request.form.get('service', '') or request.args.get('service', '')

    if service_:
        if not is_service(service_):
            return Error.INVALID_SERVICE

        srv = Service.query.filter_by(public=service_).first()
        if not srv:
            return Error.SERVICE_NOTFOUND
        return jsonify({"service": srv.as_dict()})

    if secret:
        if not is_secret(secret):
            return Error.INVALID_SECRET

        srv = Service.query.filter_by(secret=secret).first()
        if not srv:
            return Error.SERVICE_NOTFOUND
        return jsonify({"service": srv.as_dict()})

    return Error.ARGUMENT_MISSING('service')


@service.route('/service', methods=['DELETE'])
@has_secret
def service_delete(service):
    subscriptions = service.subscribed().all()
    messages = Message.query.filter_by(service=service).all()

    # In case we need to send this at a later point
    # when the subscriptions have been deleted.
    send_later = []
    if zeromq_relay_uri:
        for l in subscriptions:
            send_later.append(json_encode({'subscription': l.as_dict()}))

    map(db.session.delete, subscriptions)  # Delete all subscriptions
    map(db.session.delete, messages)  # Delete all messages
    db.session.delete(service)

    db.session.commit()

    # Notify that the subscriptions have been deleted
    if zeromq_relay_uri:
        map(queue_zmq_message, send_later)

    return Error.NONE


@service.route('/service', methods=['PATCH'])
@has_secret
def service_patch(service):
    fields = ['name', 'icon']
    updated = False

    for field in fields:
        data = request.form.get(field, '').strip()
        if data is not '':
            setattr(service, field, data)
            updated = True

    if updated:
        db.session.commit()
        return Error.NONE
    else:
        return Error.NO_CHANGES
