#!/usr/bin/env python
import roslib
import nxt
import thread
import time

roslib.load_manifest('robair_driver')

import rospy

from robair_msgs.msg import Command


class NxtNode(object):
    '''Robair nxt node'''
    def __init__(self, node_name="nxt"):
        self.node_name = node_name
        rospy.init_node('nxt')
        rospy.Subscriber('/cmd', Command, self.new_cmd)

    def new_cmd(self, cmd):
        print(cmd)


if __name__ == '__main__':
    nxt_node = NxtNode()
    rospy.loginfo("%s running..." % nxt_node.node_name)
    # nxt_node.main_loop()
    rospy.spin()
    rospy.loginfo("%s stopped." % nxt_node.node_name)
