#!/usr/bin/env python
import roslib

roslib.load_manifest('robair_app')

import rospy

rospy.set_param('logger_level', 'None')
rospy.set_param('robot_jabber_id', 'robair@im.quicker.fr')
rospy.set_param('robot_jabber_password', 'robair')
rospy.set_param('tv_jabber_id', 'tv@im.quicker.fr')
rospy.set_param('tv_jabber_password', 'tv')

import unittest
from robair_app.xmpp.client import ClientXMPP
from robair_app.xmpp.rpc import remote


class Server(ClientXMPP):
    def __init__(self):
        jid = rospy.get_param('robot_jabber_id')
        password = rospy.get_param('robot_jabber_password')
        super(Server, self).__init__(jid, password)

    @remote
    def div(self, a, b):
        return a / b

    @remote
    def echo(self, message):
        return message

    @remote
    def add(self, *args):
        return sum((int(i) for i in args))

    @remote
    def whoami(self):
        return self.current_rpc_session().client_jid


class Client(ClientXMPP):
    def __init__(self):
        jid = rospy.get_param('tv_jabber_id', 'tv@im.quicker.fr')
        password = rospy.get_param('tv_jabber_password', 'tv')
        super(Client, self).__init__(jid, password)
        self.robot_jid = rospy.get_param('robot_jabber_id')
        self.proxy = self.get_proxy(self.robot_jid)


## A sample python unit test
class TestXmppRPC(unittest.TestCase):
    def setUp(self):
        self.server = Server()
        self.client = Client()

    def tearDown(self):
        self.server.disconnect()
        self.client.disconnect()

    def test_echo(self):
        self.assertEquals(self.client.proxy.echo(message="test"), "test")

    def test_add(self):
        self.assertEquals(self.client.proxy.add(3, 3, 3), 9)

if __name__ == '__main__':
    import rosunit
    rosunit.unitrun('robair_app', 'test_xmpp_rpc', TestXmppRPC)
