import rospy
import requests
from robair_msgs.msg import Command

from robair_common import log
from robair_common.utils import get_local_ip_address

from .xmpp.client import ClientXMPP
from .xmpp.rpc import remote
from .player import run_player


class RobotManager(ClientXMPP):
    def __init__(self, node_name):
        rospy.init_node(node_name)
        jid = rospy.get_param('robot_jabber_id')
        password = rospy.get_param('robot_jabber_password')
        super(RobotManager, self).__init__(jid, password)
        self.cmd_publisher = rospy.Publisher('/cmd', Command)
        self.clients = {}

    @remote
    def hello(self, key):
        url = rospy.get_param('robair_api_url')
        r = requests.get(url + "check", params={"key": key})
        authorize = r.json()['valid']
        if r.json()['valid']:
            jid = self.current_rpc_session().client_jid
            self.clients[jid] = self.get_proxy(jid)
            run_player(self.get_url_streaming(),
                       self.clients[jid].get_url_streaming())
        return authorize

    def forward_distance(self, distance):
        for client in self.clients.values():
            client.publish_distance(distance)

    @remote
    def get_url_streaming(self):
        # Improve this with ROS srv...
        return "http://%s:%d" % (get_local_ip_address(), 9090)

    @remote
    def publish_cmd(self, cmd):
        jid = self.current_rpc_session().client_jid
        if jid in self.clients:
            self.cmd_publisher.publish(cmd)
            return True


class ClientManager(ClientXMPP):
    def __init__(self, node_name):
        jid = rospy.get_param('tv_jabber_id')
        password = rospy.get_param('tv_jabber_password')
        super(ClientManager, self).__init__(jid, password)
        rospy.init_node(node_name)
        self.robot_jid = rospy.get_param('robot_jabber_id')
        self.proxy_robot = self.get_proxy(self.robot_jid)
        if not self.proxy_robot.hello(self.make_reservation()):
            raise RuntimeError('RobAir permission denied, try later...')
        run_player(self.get_url_streaming(),
                   self.proxy_robot.get_url_streaming())
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

    @remote
    def get_url_streaming(self):
        # Improve this with ROS srv...
        return "http://%s:%d" % (get_local_ip_address(), 9090)
