#!/usr/bin/env python
from __future__ import division
import roslib

roslib.load_manifest('robair_driver')

import rospy
from std_msgs.msg import String


class NetworkNode():
    '''Robair network node'''
    def __init__(self, interfaces, topic, pubrate=10, node_name='network'):
        self.node_name = node_name
        rospy.init_node(self.node_name)
        self.pub = rospy.Publisher(topic, String)
        self.interfaces = interfaces
        self.time_sleep = 1 / pubrate if pubrate != 0 else 1

    def _roaming(self):
        self.best_interface = self.interfaces[0]

    def main_loop(self):
        while not rospy.is_shutdown():
            self._roaming()
            # publish interface with the best signal quality
            self.pub.publish(self.best_interface)
            rospy.sleep(self.time_sleep)


if __name__ == '__main__':
    wifi_node = NetworkNode(['wlan0', 'wlan1'], '/info/network')
    rospy.loginfo("%s running..." % wifi_node.node_name)
    wifi_node.main_loop()
    rospy.loginfo("%s stopped." % wifi_node.node_name)
