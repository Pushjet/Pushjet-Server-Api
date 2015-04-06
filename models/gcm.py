from shared import db
import urllib2
from json import dumps
from sqlalchemy.dialects.mysql import INTEGER
from datetime import datetime
from config import google_api_key
from models import Listen, Message

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
        return '<Gcm %r>' % self.uuid

    def as_dict(self):
        data = {
            "uuid": self.service.as_dict(),
            "gcm_registration_id": self.gcmId,
            "timestamp": int(self.timestamp_created.strftime('%s')),
        }
        return data

    @staticmethod
    def send_message(message):
        """

        :type message: Message
        """
        listeners = Listen.query.filter_by(service=message.service).all()
        if len(listeners) == 0:
            return 0
        gcm_filter = Gcm.query.filter(Gcm.uuid.in_([l.device for l in listeners]))
        registration_ids = [g.gcmid for g in gcm_filter.all()]
        if len(registration_ids) > 0:
            data = dumps({
                "registration_ids": registration_ids,
                "data": {"message": message.as_dict()},
            })
            headers = {
                'Authorization': 'key=%s' % google_api_key,
                'Content-Type': 'application/json',
            }
            req = urllib2.Request('https://android.googleapis.com/gcm/send', data, headers)
            urllib2.urlopen(req).read()
            uuids = [g.uuid for g in gcm_filter.all()]
            gcm_listens = Listen.query.filter_by(service=message.service).filter(Listen.device.in_(uuids)).all()
            for l in gcm_listens:
                l.timestamp_checked = datetime.utcnow()
            db.session.commit()
        return len(registration_ids)