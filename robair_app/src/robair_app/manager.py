import rospy
import requests
from robair_msgs.msg import Command

from robair_common import log

from .xmpp.client import ClientXMPP
from .xmpp.rpc import remote


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
        self.proxy_robot.hello(self.make_reservation())
        # subscriber to a remote cmd
        rospy.Subscriber('/cmd', Command, self.proxy_robot.publish_cmd)

    def make_reservation(self):
        url = rospy.get_param('robair_api_url')
        r = requests.get(url + "new", params={"jid": self.jid})
        data = r.json()
        if data['error']:
            log.info("Error: %s" % data['error_message'])
        else:
            return data['key']

    def publish_battery_state(self, data):
        pass
