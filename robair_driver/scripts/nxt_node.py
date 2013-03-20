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
    def __init__(self, node_name="nxt_motion_control"):
        self.node_name = node_name
        rospy.init_node(self.node_name)
        rospy.Subscriber('/cmd', Command, self.new_cmd_callback)
        self.current_cmd = Command(0, 0)
        self.brick = nxt.find_one_brick()
        self.motor_a = nxt.Motor(self.brick, nxt.PORT_A)
        self.motor_b = nxt.Motor(self.brick, nxt.PORT_B)

    def new_cmd_callback(self, cmd):
        if cmd.speed is None:
            cmd.speed = self.current_cmd.speed
        self.current_cmd.speed = self.current_cmd.speed + cmd.speed
        if self.current_cmd.speed < 0:
            self.current_cmd.speed = -1
        elif self.current_cmd.speed > 0:
            self.current_cmd.speed = 1
        self.current_cmd.curve = cmd.curve

    def move(self):
        speed, degrees = self.current_cmd.speed, self.current_cmd.curve
        if degrees > 0:
            if speed >= 0:
                self.motor_a.turn(80, 170)
            else:
                self.motor_b.turn(-80, 170)
        elif degrees < 0:
            if speed >= 0:
                self.motor_b.turn(80, 170)
            else:
                self.motor_a.turn(-80, 170)
        self.current_cmd.curve = 0
        if speed > 0:
            self.motor_a.run(power=70)
            self.motor_b.run(power=70)
        elif speed == 0:
            self.motor_a.idle()
            self.motor_b.idle()
        else:
            self.motor_a.run(power=-70)
            self.motor_b.run(power=-70)

    def main_loop(self):
        while not rospy.is_shutdown():
            self.move()
            time.sleep(0.1)

    def shutdown(self):
        self.motor_a.idle()
        self.motor_b.idle()


if __name__ == '__main__':
    nxt_node = NxtNode()
    rospy.loginfo("%s running..." % nxt_node.node_name)
    nxt_node.main_loop()
    nxt_node.shutdown()
    rospy.loginfo("%s stopped." % nxt_node.node_name)
