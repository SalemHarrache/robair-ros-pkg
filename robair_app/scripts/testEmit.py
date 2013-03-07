#!/usr/bin/env python

from __future__ import division
import roslib

roslib.load_manifest('robair_app')

import rospy
from robair_msgs.msg import Command


class EmitCmdNode():
    '''Robair EmitCmdNode node'''
    def __init__(self, topic='/cmd/random', pubrate=10):
        self.pub = rospy.Publisher(topic, Command)
        rospy.init_node('EmitCmd')
        # fake battery states generator
        self.time_sleep = 1 / pubrate if pubrate != 0 else 1

    @property
    def gen_random_cmd(self):
        return Command(speed=6, angle=63)

    def main_loop(self):
        while not rospy.is_shutdown():
            self.pub.publish(self.gen_random_cmd)
            rospy.sleep(self.time_sleep)


if __name__ == '__main__':
    emit_cmd_node = EmitCmdNode()
    emit_cmd_node.main_loop()
