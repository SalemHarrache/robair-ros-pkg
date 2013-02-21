import logging
import rospy
from sleekxmpp import ClientXMPP


class RobBot(ClientXMPP):

    def __init__(self, jid, password):
        super(RobBot, self).__init__(jid, password)
        rospy.init_node('robbot')
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.echo_answer)
        self.load_plugin()
        logging.basicConfig()

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def echo_answer(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply(msg['body']).send()

    def send_message(self, dest, mbody):
        super(RobBot, self).send_message(mto=dest, mbody=mbody, mtype='chat')

    def load_plugin(self):
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0060')  # PubSub
        self.register_plugin('xep_0199')  # XMPP Ping
        self.auto_reconnect = True
