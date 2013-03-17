#!/usr/bin/env python
import roslib

roslib.load_manifest('robair_app')

import rospy
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
        self.client = Client()

    def test_echo(self):
        self.assertEquals(self.client.proxy.echo(message="test"), "test")


if __name__ == '__main__':
    import rosunit
    rospy.set_param('logger_level', 'DEBUG')
    rospy.set_param('robot_jabber_id', 'robot@im.quicker.fr')
    rospy.set_param('robot_jabber_password', 'robot')
    rospy.set_param('tv_jabber_id', 'tv@im.quicker.fr')
    rospy.set_param('tv_jabber_password', 'tv')
    rosunit.unitrun('robair_app', 'test_xmpp_rpc', TestXmppRPC)
