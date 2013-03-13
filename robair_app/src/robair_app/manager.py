import rospy
from .xmpp import BotXMPP, remote
# from robair_msgs.msg import Command


class RobBot(BotXMPP):
    def __init__(self, node_name):
        jid = rospy.get_param('robot_jabber_id')
        password = rospy.get_param('robot_jabber_password')
        super(RobBot, self).__init__(jid, password, node_name)

    @remote
    def echo(self, message):
        return message

    @remote
    def add(self, *args):
        return sum([int(i) for i in args])


class ClientBot(BotXMPP):
    def __init__(self, node_name):
        jid = rospy.get_param('tv_jabber_id')
        password = rospy.get_param('tv_jabber_password')
        self.robot_jid = rospy.get_param('robot_jabber_id')
        super(ClientBot, self).__init__(jid, password, node_name)
        self.robbot_proxy = self.get_proxy(self.robot_jid)



    #     self.topic_name = "/info/battery"
    #     rospy.Subscriber(self.topic_name, Command, self.callback)
    #     rospy.spin()

    # def callback(self, data):
    #     rospy.loginfo("%s: I heard  speed %s - curve %s :D"
    #                   % (rospy.get_name(), data.speed, data.angle))
    #     topic_to_serialize = {"topic": self.topic_name, "data": data}
    #     msg = cPickle.dumps(topic_to_serialize)
    #     self.send_message(self.robot_jid, msg)
