import rospy
from robair_msgs.msg import Command
from jabberbot import JabberBot, botcmd
import cPickle as pickle


class BotXMPP(JabberBot):
    def __init__(self, jid, password, node_name):
        super(BotXMPP, self).__init__(jid, password)
        rospy.init_node(node_name)


class RobBot(BotXMPP):
    def __init__(self, node_name):
        jid = rospy.get_param('robot_jabber_id')
        password = rospy.get_param('robot_jabber_password')
        super(RobBot, self).__init__(jid, password, node_name)

    @botcmd
    def echo(self, mess, args):
        """Echo command"""
        # check key
        return "%s" % args


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
        msg = pickle.dumps(topic_to_serialize)
        self.send_message(self.robot_jid, msg)
