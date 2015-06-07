import rsa
from base64 import b64decode
from flask import Blueprint, request, jsonify
from utils import has_uuid, Error
from models import Gcm
from shared import db

gcm = Blueprint('gcm', __name__)


@gcm.route("/gcm", methods=["POST"])
@has_uuid
def gcm_register(client):
    registration = request.form.get('regid', False) or request.form.get('regId', False)
    pubkey_b64 = request.form.get('pubkey', None)
    if pubkey_b64:
        # noinspection PyBroadException
        try:
            rsa.PublicKey.load_pkcs1(b64decode(pubkey_b64), 'DER')
        except:
            return jsonify(Error.INVALID_PUBKEY)

    if not registration:
        return Error.ARGUMENT_MISSING('regid')
    regs = Gcm.query.filter_by(uuid=client).all()
    for u in regs:
        db.session.delete(u)
    reg = Gcm(client, registration, pubkey_b64)
    db.session.add(reg)
    db.session.commit()
    return jsonify(Error.NONE)


@gcm.route("/gcm", methods=["DELETE"])
@has_uuid
def gcm_unregister(client):
    regs = Gcm.query.filter_by(uuid=client).all()
    for u in regs:
        db.session.delete(u)
    db.session.commit()
    return jsonify(Error.NONE)

