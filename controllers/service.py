from flask import Blueprint, jsonify, request
from utils import Error, is_service, is_secret
from models import Service
from shared import db

service = Blueprint('service', __name__)


@service.route('/service', methods=["POST"])
def service_create():
    name = request.form.get('name', '').strip()
    icon = request.form.get('icon', '').strip()
    if not name:
        return jsonify(Error.ARGUMENT_MISSING('name'))
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
            return jsonify(Error.INVALID_SERVICE)

        srv = Service.query.filter_by(public=service_).first()
        if not srv:
            return jsonify(Error.SERVICE_NOTFOUND)
        return jsonify({"service": srv.as_dict()})

    if secret:
        if not is_secret(secret):
            return jsonify(Error.INVALID_SECRET)

        srv = Service.query.filter_by(secret=secret).first()
        if not srv:
            return jsonify(Error.SERVICE_NOTFOUND)
        return jsonify({"service": srv.as_dict()})

    return jsonify(Error.ARGUMENT_MISSING('service'))
