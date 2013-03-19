import rospy
from .xmpp.client import ClientXMPP
from .xmpp.rpc import remote
from robair_msgs.msg import Command


class RobotManager(ClientXMPP):
    def __init__(self, node_name):
        rospy.init_node(node_name)
        jid = rospy.get_param('robot_jabber_id')
        password = rospy.get_param('robot_jabber_password')
        super(RobotManager, self).__init__(jid, password)
        self.cmd_publisher = rospy.Publisher('/cmd', Command)
        self.clients = {}

    @remote
    def publish_cmd(self, cmd):
        self.cmd_publisher.publish(cmd)

    @remote
    def hello(self, key):
        session = self.current_rpc_session()
        self.clients[session.client_jid] = True
        return True


class ClientManager(ClientXMPP):
    def __init__(self, node_name):
        jid = rospy.get_param('tv_jabber_id')
        password = rospy.get_param('tv_jabber_password')
        super(ClientManager, self).__init__(jid, password)
        rospy.init_node(node_name)
        self.robot_jid = rospy.get_param('robot_jabber_id')
        self.proxy_robot = self.get_proxy(self.robot_jid)
        rospy.Subscriber('/cmd', Command, self.proxy_robot.publish_cmd)
