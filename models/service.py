from shared import db
from datetime import datetime
from sqlalchemy.dialects.mysql import INTEGER
import hashlib
from os import urandom
from .listen import Listen
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
        return '<Service %r>' % self.name

    def cleanup(self, commit=True):
        threshold = self.listening().order_by(Listen.timestamp_checked.asc()).first()
        threshold = datetime(3000, 1, 1) if not threshold else threshold.timestamp_checked

        messages = Message.query \
            .filter_by(service=self) \
            .filter(threshold > Message.timestamp_created) \
            .all()

        for msg in messages:
            db.session.delete(msg)
        if commit:
            db.session.commit()

    def listening(self):
        return Listen.query.filter_by(service=self)

    def as_dict(self, secret=False):
        data = {
            "public": self.public,
            "name": self.name,
            "created": int(self.timestamp_created.strftime("%s")),
            "icon": self.icon,
        }
        if secret:
            data["secret"] = self.secret
        return data
