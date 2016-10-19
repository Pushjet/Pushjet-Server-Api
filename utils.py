from re import compile
from json import dumps
from flask import request, jsonify
from functools import wraps
from models import Service
from shared import zmq_relay_socket

uuid = compile(r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$')
service = compile(r'^[a-zA-Z0-9]{4}-[a-zA-Z0-9]{6}-[a-zA-Z0-9]{12}-[a-zA-Z0-9]{5}-[a-zA-Z0-9]{9}$')
is_uuid = lambda s: uuid.match(s) is not None
is_service = lambda s: service.match(s) is not None
is_secret = lambda s: compile(r'^[a-zA-Z0-9]{32}$').match(s) is not None

QUERY_ACTION_NEW_MESSAGE = 0
QUERY_UPDATE_LISTEN = 1


class Error(object):
    @staticmethod
    def _e(message, error_code, http_status):
        return (dumps({'error': {'message': message, 'id': error_code}}), http_status)

    NONE = (dumps({'status': 'ok'}), 200) # OK
    INVALID_CLIENT = _e.__func__('Invalid client uuid', 1, 400) # Bad request
    INVALID_SERVICE = _e.__func__('Invalid service', 2, 400) # - || -
    INVALID_SECRET = _e.__func__('Invalid secret', 3, 400) # - || -
    DUPLICATE_LISTEN = _e.__func__('Already subscribed to that service', 4, 409) # Conflict
    RATE_TOOFAST = _e.__func__('Whoaw there cowboy, slow down!', 5, 429) # Too many requests
    SERVICE_NOTFOUND = _e.__func__('Service not found', 6, 404)
    INVALID_PUBKEY = _e.__func__('Invalid public key supplied. Please send a DER formatted base64 encoded key.', 8, 400) # Bad request
    CONNECTION_CLOSING = _e.__func__('Connection closing', 9, 499) # Client closed request
    NO_CHANGES = _e.__func__('No changes were made', 10, 400) # Bad request
    NOT_SUBSCRIBED = _e.__func__('Not subscribed to that service', 11, 409) # Conflict

    @staticmethod
    def ARGUMENT_MISSING(arg):
        return Error._e('Missing argument {}'.format(arg), 7, 400) # Bad request


def has_uuid(f):
    @wraps(f)
    def df(*args, **kwargs):
        client = request.form.get('uuid', '') or request.args.get('uuid', '')
        if not client:
            return Error.ARGUMENT_MISSING('uuid')
        if not is_uuid(client):
            return Error.INVALID_CLIENT
        return f(*args, client=client, **kwargs)

    return df


def has_service(f):
    @wraps(f)
    def df(*args, **kwargs):
        service = request.form.get('service', '') or request.args.get('service', '')
        if not service:
            return Error.ARGUMENT_MISSING('service')
        if not is_service(service):
            return Error.INVALID_SERVICE

        srv = Service.query.filter_by(public=service).first()
        if not srv:
            return Error.SERVICE_NOTFOUND
        return f(*args, service=srv, **kwargs)

    return df


def has_secret(f):
    @wraps(f)
    def df(*args, **kwargs):
        secret = request.form.get('secret', '') or request.args.get('secret', '')
        if not secret:
            return Error.ARGUMENT_MISSING('secret')
        if not is_secret(secret):
            return Error.INVALID_SECRET

        srv = Service.query.filter_by(secret=secret).first()
        if not srv:
            return Error.SERVICE_NOTFOUND
        return f(*args, service=srv, **kwargs)

    return df


def queue_zmq_message(message):
    zmq_relay_socket.send_string(message)
