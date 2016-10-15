from flask import Blueprint, request, jsonify
from utils import has_uuid, Error
from models import Gcm
from shared import db
from config import google_gcm_sender_id

gcm = Blueprint('gcm', __name__)


@gcm.route("/gcm", methods=["POST"])
@has_uuid
def gcm_register(client):
    registration = request.form.get('regid', False) or request.form.get('regId', False)

    if not registration:
        return Error.ARGUMENT_MISSING('regid')
    regs = Gcm.query.filter_by(uuid=client).all()
    for u in regs:
        db.session.delete(u)
    reg = Gcm(client, registration)
    db.session.add(reg)
    db.session.commit()
    return Error.NONE


@gcm.route("/gcm", methods=["DELETE"])
@has_uuid
def gcm_unregister(client):
    regs = Gcm.query.filter_by(uuid=client).all()
    for u in regs:
        db.session.delete(u)
    db.session.commit()
    return Error.NONE


@gcm.route("/gcm", methods=["GET"])
def gcm_sender_id():
    data = dict(sender_id=google_gcm_sender_id)
    return jsonify(data)

