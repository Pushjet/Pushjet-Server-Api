# coding=utf-8
from __future__ import unicode_literals
from application import app, limiter
from uuid import uuid4
import os
import unittest
import string
import random
import json
import sys

if not os.path.exists('config.py'):
    sys.exit('Please copy config.example.py to config.py and configure it')
import config


class PushjetTestCase(unittest.TestCase):
    def setUp(self):
        self.uuid = str(uuid4())
        app.config['TESTING'] = True
        limiter.enabled = False
        self.app = app.test_client()
        config.google_api_key = config.google_api_key or 'PLACEHOLDER'

    def _random_str(self, length=10, append_unicode=True):
        # A random string with the "cupcake" in Japanese appended to it
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length)) \
               + (u'カップケーキ' if append_unicode else '')

    def _failing_loader(self, s):
        data = json.loads(s)
        if 'error' in data:
            err = data['error']
            print "Got an unexpected error, [%i] %s" % (err['id'], err['message'])
            assert False
        return data

    def test_service_create(self):
        name = "Hello test! %s" % self._random_str(5)
        data = {
            "name": name,
            "icon": "http://i.imgur.com/%s.png" % self._random_str(7, False)
        }
        rv = self.app.post('/service', data=data)
        resp = json.loads(rv.data)
        assert 'service' in resp
        return resp['service']['public'], resp['service']['secret'], name

    def test_listen_new(self):
        public, secret, name = self.test_service_create()
        data = {"uuid": self.uuid, "service": public}
        rv = self.app.post('/listen', data=data)
        self._failing_loader(rv.data)
        return public, secret

    def test_listen_delete(self):
        public, secret = self.test_listen_new()
        rv = self.app.delete('/listen?uuid=%s&service=%s' % (self.uuid, public))
        self._failing_loader(rv.data)

    def test_listen_list(self):
        public, secret = self.test_listen_new()
        rv = self.app.get('/listen?uuid=%s' % self.uuid)
        resp = self._failing_loader(rv.data)
        assert 'listens' in resp
        assert len(resp['listens']) == 1
        assert resp['listens'][0]['service']['public'] == public

    def test_message_send(self, public='', secret=''):
        if not public or not secret:
            public, secret = self.test_listen_new()
        data = {
            "level": random.randint(0, 5),
            "message": "Test message - %s" % self._random_str(20),
            "title": "Test Title - %s" % self._random_str(5),
            "secret": secret,
        }
        rv = self.app.post('/message', data=data)
        self._failing_loader(rv.data)
        return public, secret, data

    def test_message_receive(self, minimum=1):
        self.test_message_send()
        rv = self.app.get('/message?uuid=%s' % self.uuid)
        resp = self._failing_loader(rv.data)
        assert len(resp['messages']) >= minimum
        rv = self.app.get('/message?uuid=%s' % self.uuid)
        resp = self._failing_loader(rv.data)
        assert len(resp['messages']) == 0

    def test_message_receive_multi(self):
        # Stress test it a bit
        for _ in range(10):
            public, secret, msg = self.test_message_send()
            for __ in range(5):
                self.test_message_send(public, secret)
        self.test_message_receive(50)  # We sent at least 50 messages

    def test_message_read(self):
        self.test_message_send()
        rv = self.app.delete('/message?uuid=%s' % self.uuid)
        rv = self.app.get('/message?uuid=%s' % self.uuid)
        resp = self._failing_loader(rv.data)
        assert len(resp['messages']) == 0

    def test_message_read_multi(self):
        # Stress test it a bit
        for _ in range(10):
            public, secret, msg = self.test_message_send()
            for __ in range(50):
                self.test_message_send(public, secret)
        self.test_message_read()

    def test_service_delete(self):
        public, secret = self.test_listen_new()
        # Send a couple of messages, these should be deleted
        for _ in range(10):
            self.test_message_send(public, secret)

        rv = self.app.delete('/service?secret=%s' % secret)
        self._failing_loader(rv.data)

        # Does the service not exist anymore?
        rv = self.app.get('/service?service=%s' % public)
        assert 'error' in json.loads(rv.data)

        # Has the listener been deleted?
        rv = self.app.get('/listen?uuid=%s' % self.uuid)
        resp = self._failing_loader(rv.data)
        assert public not in [l['service']['public'] for l in resp['listens']]

    def test_service_info(self):
        public, secret, name = self.test_service_create()
        rv = self.app.get('/service?service=%s' % public)
        data = self._failing_loader(rv.data)
        assert 'service' in data
        srv = data['service']
        assert srv['name'] == name
        assert srv['public'] == public

    def test_service_info_secret(self):
        public, secret, name = self.test_service_create()
        rv = self.app.get('/service?secret=%s' % secret)
        data = self._failing_loader(rv.data)
        assert 'service' in data
        srv = data['service']
        assert srv['name'] == name
        assert srv['public'] == public

    def test_uuid_regex(self):
        rv = self.app.get('/service?service=%s' % self._random_str(20))
        assert 'error' in json.loads(rv.data)

    def test_service_regex(self):
        rv = self.app.get('/message?uuid=%s' % self._random_str(20))
        assert 'error' in json.loads(rv.data)

    def test_missing_arg(self):
        rv = self.app.get('/message')
        assert 'error' in json.loads(rv.data) and '7' in rv.data
        rv = self.app.get('/service')
        assert 'error' in json.loads(rv.data) and '7' in rv.data

    def test_gcm_register(self):
        self.app.post('/gcm', data={'uuid': self.uuid, 'regId': self._random_str(40)})


if __name__ == '__main__':
    unittest.main()
