import logging
import rospy
from sleekxmpp import ClientXMPP
from robair_msgs.msg import Command
import cPickle


class BotXMPP(ClientXMPP):
    def __init__(self, jid, password, node_name):
        super(BotXMPP, self).__init__(jid, password)
        rospy.init_node(node_name)
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message_handler)
        self.load_plugin()
        logging.basicConfig()

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def message_handler(self, msg):
        print(msg['body'])
        topic_data = cPickle.loads(msg)
        self.pub = rospy.Publisher(topic_data.topic, topic_data.data)

    def send_message(self, dest, mbody):
        super(BotXMPP, self).send_message(mto=dest, mbody=mbody, mtype='chat')

    def load_plugin(self):
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0060')  # PubSub
        self.register_plugin('xep_0199')  # XMPP Ping
        self.auto_reconnect = True


class RobBot(BotXMPP):
    def __init__(self, node_name):
        jid = rospy.get_param('robot_jabber_id')
        password = rospy.get_param('robot_jabber_password')
        super(RobBot, self).__init__(jid, password, node_name)

    def message_handler(self, msg):
        # echo serveur
        if msg['type'] in ('chat', 'normal'):
            msg.reply(msg['body']).send()


class ClientBot(BotXMPP):
    def __init__(self, node_name):
        jid = rospy.get_param('tv_jabber_id')
        password = rospy.get_param('tv_jabber_password')
        self.robot_jid = rospy.get_param('robot_jabber_id')
        super(ClientBot, self).__init__(jid, password, node_name)

        self.topic_name = "/cmd"
        rospy.Subscriber(self.topic_name, Command, self.callback)
        rospy.spin()

    def callback(self, data):
        rospy.loginfo("%s: I heard  speed %s - curve %s :D"
                      % (rospy.get_name(), data.speed, data.angle))
        topic_to_serialize = {"topic": self.topic_name, "data": data}
        msg = cPickle.dumps(topic_to_serialize)
        self.send_message(self.robot_jid, msg)
