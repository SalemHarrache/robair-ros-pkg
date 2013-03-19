#!/usr/bin/env python
import roslib
import nxt
# import thread
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
        self.current_cmd = Command(0, 0)
        self.brick = nxt.find_one_brick()
        self.motor_a = nxt.Motor(self.brick, nxt.PORT_A)
        self.motor_b = nxt.Motor(self.brick, nxt.PORT_B)

    def new_cmd(self, cmd):
        if cmd.speed is None:
            cmd.speed = self.current_cmd.speed
        self.current_cmd = cmd

    def main_loop(self):
        while not rospy.is_shutdown():
            speed, degrees = self.current_cmd.speed, self.current_cmd.curve
            if speed > 0:
                self.motor_a.run(power=65)
                self.motor_b.run(power=65)
            else:
                self.motor_a.idle()
                self.motor_b.idle()
            time.sleep(0.1)

if __name__ == '__main__':
    nxt_node = NxtNode()
    rospy.loginfo("%s running..." % nxt_node.node_name)
    nxt_node.main_loop()
    rospy.spin()
    rospy.loginfo("%s stopped." % nxt_node.node_name)
