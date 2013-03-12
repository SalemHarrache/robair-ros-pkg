#!/usr/bin/env python
import roslib

roslib.load_manifest('robair_driver')

import rospy

from robair_msgs.msg import Command
from robair_driver import keylogger


class KeyboardNode(object):
    '''Robair keyboard node'''
    def __init__(self, topic='/cmd', node_name="keyboard"):
        self.node_name = node_name
        self.pub = rospy.Publisher(topic, Command)
        rospy.init_node('keyboard')

    def main_loop(self):
        done = lambda: rospy.is_shutdown()
        keylogger.log(done, self.key_pressed)

    def key_pressed(self, dtime, modifiers, key):
        directions = {"top": (1, 0), "bottom": (-1, 0),
                      "left": (None, 1), "right": (1, 90)}
        if key in directions.keys():
            self.pub.publish(Command(*directions[key]))


if __name__ == '__main__':
    keyboard_node = KeyboardNode()
    rospy.loginfo("%s running..." % keyboard_node.node_name)
    keyboard_node.main_loop()
    rospy.loginfo("%s stopped." % keyboard_node.node_name)
