#!/usr/bin/env python
import roslib
import nxt
# import thread
import time

roslib.load_manifest('robair_driver')

import rospy
from std_msgs.msg import String
from robair_driver.nxt_brick import brick


class NxtUltrasonicNode(object):
    '''Robair nxt node'''
    def __init__(self, node_name="nxt_ultrasonic"):
        self.node_name = node_name
        self.pub = rospy.Publisher('/info/ultrasonic', String)
        rospy.init_node(self.node_name)
        self.ultrasonic = nxt.Ultrasonic(brick, nxt.PORT_4)

    def main_loop(self):
        while not rospy.is_shutdown():
            self.pub.publish("%s" % self.ultrasonic.get_sample())
            time.sleep(0.2)

if __name__ == '__main__':
    nxt_node = NxtUltrasonicNode()
    rospy.loginfo("%s running..." % nxt_node.node_name)
    nxt_node.main_loop()
    rospy.loginfo("%s stopped." % nxt_node.node_name)
