from shared import db
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER, TINYINT


class Message(db.Model):
    id = db.Column(INTEGER(unsigned=True), primary_key=True)
    service_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('service.id'), nullable=False)
    service = db.relationship('Service', backref=db.backref('message', lazy='dynamic'))
    text = db.Column(db.TEXT, nullable=False)
    title = db.Column(db.VARCHAR)
    level = db.Column(TINYINT, nullable=False, default=0)
    link = db.Column(db.TEXT, nullable=False, default='')
    timestamp_created = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __init__(self, service, text, title=None, level=0, link=''):
        self.service = service
        self.text = text
        self.title = title
        self.level = level
        self.link = link

    def __repr__(self):
        return '<Message {}>'.format(self.id)

    def as_dict(self):
        return {
            "service": self.service.as_dict(),
            "message": self.text,
            "title": self.title,
            "link": self.link,
            "level": self.level,
            "timestamp": int((self.timestamp_created - datetime.utcfromtimestamp(0)).total_seconds())
        }
