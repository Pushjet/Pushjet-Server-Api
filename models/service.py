from shared import db
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER
import hashlib
from os import urandom
from .subscription import Subscription
from .message import Message


class Service(db.Model):
    id = db.Column(INTEGER(unsigned=True), primary_key=True)
    secret = db.Column(db.VARCHAR(32), nullable=False)
    public = db.Column(db.VARCHAR(40), nullable=False)
    name = db.Column(db.VARCHAR(255), nullable=False)
    icon = db.Column(db.TEXT, nullable=False, default='')
    timestamp_created = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __init__(self, name, icon=''):
        self.secret = hashlib.sha1(urandom(100)).hexdigest()[:32]
        self.name = name
        self.icon = icon
        pub = list(hashlib.new('ripemd160', self.secret).hexdigest())[:40]
        sep = [4, 11, 24, 30]
        for s in sep:
            pub[s] = '-'
        self.public = ''.join(pub)

    def __repr__(self):
        return '<Service {}: {}>'.format(self.id, self.name)

    def cleanup(self):
        threshold = self.subscribed().order_by(Subscription.last_read.asc()).first().last_read

        # Nothing to do
        if not threshold:
            return

        messages = Message.query \
            .filter_by(service=self) \
            .filter(threshold > Message.id) \
            .all()

        map(db.session.delete, messages)

    def subscribed(self):
        return Subscription.query.filter_by(service=self)

    def as_dict(self, secret=False):
        data = {
            "public": self.public,
            "name": self.name,
            "created": int((self.timestamp_created - datetime.utcfromtimestamp(0)).total_seconds()),
            "icon": self.icon,
        }
        if secret:
            data["secret"] = self.secret
        return data
