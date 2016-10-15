from flask import current_app
from shared import db
from sqlalchemy.dialects.mysql import INTEGER
from datetime import datetime
from config import google_api_key
from models import Subscription, Message
import requests

gcm_url = 'https://android.googleapis.com/gcm/send'


class Gcm(db.Model):
    id = db.Column(INTEGER(unsigned=True), primary_key=True)
    uuid = db.Column(db.VARCHAR(40), nullable=False)
    gcmid = db.Column(db.TEXT, nullable=False)
    timestamp_created = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __init__(self, device, gcmid):
        self.uuid = device
        self.gcmid = gcmid

    def __repr__(self):
        return '<Gcm {}>'.format(self.uuid)

    def as_dict(self):
        data = {
            "uuid": self.service.as_dict(),
            "gcm_registration_id": self.gcmId,
            "timestamp": int((self.timestamp_created - datetime.utcfromtimestamp(0)).total_seconds()),
        }
        return data

    @staticmethod
    def send_message(message):
        """

        :type message: Message
        """
        subscriptions = Subscription.query.filter_by(service=message.service).all()
        if len(subscriptions) == 0:
            return 0
        gcm_devices = Gcm.query.filter(Gcm.uuid.in_([l.device for l in subscriptions])).all()

        if len(gcm_devices) > 0:
            data = dict(message=message.as_dict(), encrypted=False)
            Gcm.gcm_send([r.gcmid for r in gcm_devices], data)

        if len(gcm_devices) > 0:
            uuids = [g.uuid for g in gcm_devices]
            gcm_subscriptions = Subscription.query.filter_by(service=message.service).filter(Subscription.device.in_(uuids)).all()
            last_message = Message.query.order_by(Message.id.desc()).first()
            for l in gcm_subscriptions:
                l.timestamp_checked = datetime.utcnow()
                l.last_read = last_message.id if last_message else 0
            db.session.commit()
        return len(gcm_devices)

    @staticmethod
    def gcm_send(ids, data):
        url = 'https://android.googleapis.com/gcm/send'
        headers = dict(Authorization='key={}'.format(google_api_key))
        data = dict(registration_ids=ids, data=data)

        if current_app.config['TESTING'] is True:
            current_app.config['TESTING_GCM'].append(data)
        else:
            requests.post(url, json=data, headers=headers)
