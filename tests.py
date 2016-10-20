# coding=utf-8
from __future__ import unicode_literals

import os
from uuid import uuid4
import unittest
import string
import random
import json
import sys

try:
    import config
except ImportError:
    sys.exit('Please copy config.example.py to config.py and configure it')


class PushjetTestCase(unittest.TestCase):
    def setUp(self):
        config.google_api_key = config.google_api_key or 'PLACEHOLDER'

        self.uuid = str(uuid4())
        from application import app

        app.config['TESTING'] = True
        app.config['TESTING_GCM'] = []

        self.gcm = app.config['TESTING_GCM']
        self.app = app.test_client()
        self.app_real = app

    def _random_str(self, length=10, unicode=True):
        # A random string with the "cupcake" in Japanese appended to it
        # Always make sure that there is some unicode in there
        random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

        if unicode:
            random_str = random_str[:-7] + 'カップケーキ'
            # It's important that the following is a 4+-byte Unicode character.
            random_str = '😉' + random_str

        return random_str

    def _failing_loader(self, s):
        data = json.loads(s)
        if 'error' in data:
            err = data['error']
            raise AssertionError("Got an unexpected error, [{}] {}".format(err['id'], err['message']))

        return data

    def test_service_create(self):
        name = "Hello test! {}".format(self._random_str(5))
        data = {
            "name": name,
            "icon": "http://i.imgur.com/{}.png".format(self._random_str(7, False))
        }
        rv = json.loads(self.app.post('/service', data=data).data)
        assert 'service' in rv
        return rv['service']['public'], rv['service']['secret'], name

    def test_subscription_new(self):
        public, secret, name = self.test_service_create()
        data = dict(uuid=self.uuid, service=public)
        rv = self.app.post('/subscription', data=data)
        self._failing_loader(rv.data)
        return public, secret

    def test_subscription_double(self):
        public, secret = self.test_subscription_new()
        data = dict(uuid=self.uuid, service=public)
        rv = self.app.post('/subscription', data=data)
        assert rv.status_code == 409
        data = json.loads(rv.data)
        assert 'error' in data
        assert data['error']['id'] == 4

    def test_subscription_delete(self):
        public, secret = self.test_subscription_new()
        rv = self.app.delete('/subscription?uuid={}&service={}'.format(self.uuid, public))
        self._failing_loader(rv.data)
        return public, secret
    
    def test_subscription_invalid_delete(self):
        # Without a just-deleted service there's a chance to get an existing
        # one, as a test database isn't created when running tests.
        public, secret = self.test_subscription_delete()
        rv = self.app.delete('/subscription?uuid={}&service={}'.format(self.uuid, public))
        assert rv.status_code == 409
        data = json.loads(rv.data)
        assert 'error' in data
        assert data['error']['id'] == 11

    def test_subscription_list(self):
        public, secret = self.test_subscription_new()
        rv = self.app.get('/subscription?uuid={}'.format(self.uuid))
        resp = self._failing_loader(rv.data)
        assert 'subscriptions' in resp
        assert len(resp['subscriptions']) == 1
        assert resp['subscriptions'][0]['service']['public'] == public

    def test_message_send(self, public='', secret=''):
        if not public or not secret:
            public, secret = self.test_subscription_new()
        data = {
            "level": random.randint(0, 5),
            "message": "Test message - {}".format(self._random_str(20)),
            "title": "Test Title - {}".format(self._random_str(5)),
            "secret": secret,
        }
        rv = self.app.post('/message', data=data)
        self._failing_loader(rv.data)
        return public, secret, data

    def test_message_send_no_subscribers(self):
        # We just want to know if the server "accepts" it
        public, secret, name = self.test_service_create()
        self.test_message_send(public, secret)

    def test_message_receive(self, amount=-1):
        if amount <= 0:
            self.test_message_send()
            amount = 1

        rv = self.app.get('/message?uuid={}'.format(self.uuid))
        resp = self._failing_loader(rv.data)
        z = len(resp['messages'])
        assert len(resp['messages']) is amount

        # Ensure it is marked as read
        rv = self.app.get('/message?uuid={}'.format(self.uuid))
        resp = self._failing_loader(rv.data)
        assert len(resp['messages']) is 0

    def test_message_receive_no_subs(self):
        self.test_message_send()
        rv = self.app.get('/message?uuid={}'.format(uuid4()))
        resp = self._failing_loader(rv.data)
        assert len(resp['messages']) is 0

    def test_message_receive_multi(self):
        self.test_message_mark_read()

        for _ in range(3):
            public, secret = self.test_subscription_new()
            for _ in range(5):
                self.test_message_send(public, secret)

        self.test_message_receive(15)

    def test_message_mark_read(self):
        self.test_message_send()
        self.app.delete('/message?uuid={}'.format(self.uuid))
        rv = self.app.get('/message?uuid={}'.format(self.uuid))
        resp = self._failing_loader(rv.data)
        assert len(resp['messages']) == 0

    def test_message_mark_read_double(self):
        self.test_message_mark_read()

        # Read again without sending
        self.app.delete('/message?uuid={}'.format(self.uuid))
        rv = self.app.get('/message?uuid={}'.format(self.uuid))
        resp = self._failing_loader(rv.data)
        assert len(resp['messages']) == 0

    def test_message_mark_read_multi(self):
        # Stress test it a bit
        for _ in range(3):
            public, secret = self.test_subscription_new()
            for _ in range(5):
                self.test_message_send(public, secret)

        self.test_message_mark_read()

    def test_service_delete(self):
        public, secret = self.test_subscription_new()
        # Send a couple of messages, these should be deleted
        for _ in range(10):
            self.test_message_send(public, secret)

        rv = self.app.delete('/service?secret={}'.format(secret))
        self._failing_loader(rv.data)

        # Does the service not exist anymore?
        rv = self.app.get('/service?service={}'.format(public))
        assert 'error' in json.loads(rv.data)

        # Has the subscriptioner been deleted?
        rv = self.app.get('/subscription?uuid={}'.format(self.uuid))
        resp = self._failing_loader(rv.data)
        assert public not in [l['service']['public'] for l in resp['subscriptions']]

    def test_service_info(self):
        public, secret, name = self.test_service_create()
        rv = self.app.get('/service?service={}'.format(public))
        data = self._failing_loader(rv.data)
        assert 'service' in data
        srv = data['service']
        assert srv['name'] == name
        assert srv['public'] == public

    def test_service_info_secret(self):
        public, secret, name = self.test_service_create()
        rv = self.app.get('/service?secret={}'.format(secret))
        data = self._failing_loader(rv.data)
        assert 'service' in data
        srv = data['service']
        assert srv['name'] == name
        assert srv['public'] == public

    def test_service_update(self):
        public, secret, name = self.test_service_create()
        data = {
            "name": self._random_str(10),
            "icon": "http://i.imgur.com/{}.png".format(self._random_str(7, False))
        }
        rv = self.app.patch('/service?secret={}'.format(secret), data=data).data
        self._failing_loader(rv)

        # Test if patched
        rv = self.app.get('/service?service={}'.format(public))
        rv = self._failing_loader(rv.data)['service']
        for key in data.keys():
            assert data[key] == rv[key]

    def test_uuid_regex(self):
        rv = self.app.get('/service?service={}'.format(self._random_str(20))).data
        assert 'error' in json.loads(rv)

    def test_service_regex(self):
        rv = self.app.get('/message?uuid={}'.format(self._random_str(20))).data
        assert 'error' in json.loads(rv)

    def test_missing_arg(self):
        rv = json.loads(self.app.get('/message').data)
        assert 'error' in rv and rv['error']['id'] is 7
        rv = json.loads(self.app.get('/service').data)
        assert 'error' in rv and rv['error']['id'] is 7

    def test_gcm_register(self):
        reg_id = self._random_str(40, unicode=False)
        data = {'uuid': self.uuid, 'regId': reg_id}
        rv = self.app.post('/gcm', data=data).data
        self._failing_loader(rv)
        return reg_id

    def test_gcm_unregister(self):
        self.test_gcm_register()
        rv = self.app.delete('/gcm', data={'uuid': self.uuid}).data
        self._failing_loader(rv)

    def test_gcm_register_double(self):
        self.test_gcm_register()
        self.test_gcm_register()

    def test_gcm_send(self):
        reg_id = self.test_gcm_register()
        public, secret, data = self.test_message_send()

        messages = [m['data'] for m in self.gcm
                    if reg_id in m['registration_ids']]

        assert len(messages) is 1
        assert messages[0]['encrypted'] is False

        message = messages[0]['message']
        assert message['service']['public'] == public
        assert message['message'] == data['message']

#    def test_get_version(self):
#        version = self.app.get('/version').data
#
#        assert len(version) is 7
#        with open('.git/refs/heads/master', 'r') as f:
#            assert f.read()[:7] == version

    def test_get_static(self):
        files = ['robots.txt', 'favicon.ico']

        for f in files:
            path = os.path.join(self.app_real.root_path, 'static', f)
            with open(path, 'rb') as i:
                data = self.app.get('/{}'.format(f)).data
                assert data == i.read()


if __name__ == '__main__':
    unittest.main()
