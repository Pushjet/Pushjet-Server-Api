from shared import db
from sqlalchemy.dialects.mysql import INTEGER
from datetime import datetime
from .message import Message


class Subscription(db.Model):
    id = db.Column(INTEGER(unsigned=True), primary_key=True)
    device = db.Column(db.VARCHAR(40), nullable=False)
    service_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('service.id'), nullable=False)
    service = db.relationship('Service', backref=db.backref('subscription', lazy='dynamic'))
    last_read = db.Column(INTEGER(unsigned=True), db.ForeignKey('message.id'), default=0)
    timestamp_created = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    timestamp_checked = db.Column(db.TIMESTAMP)

    def __init__(self, device, service):
        last_message = Message.query.order_by(Message.id.desc()).first()

        self.device = device
        self.service = service
        self.timestamp_checked = datetime.utcnow()
        self.last_read = last_message.id if last_message else 0

    def __repr__(self):
        return '<Subscription {}>'.format(self.id)

    def messages(self):
        return Message.query \
            .filter_by(service_id=self.service_id) \
            .filter(Message.id > self.last_read)

    def as_dict(self):
        data = {
            "uuid": self.device,
            "service": self.service.as_dict(),
            "timestamp": int((self.timestamp_created - datetime.utcfromtimestamp(0)).total_seconds()),
            "timestamp_checked": int((self.timestamp_checked - datetime.utcfromtimestamp(0)).total_seconds())
        }
        return data
