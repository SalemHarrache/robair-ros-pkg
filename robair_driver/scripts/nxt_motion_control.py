#!/usr/bin/env python
import roslib
import nxt
# import thread
import time

roslib.load_manifest('robair_driver')

import rospy

from robair_msgs.msg import Command
from robair_driver.nxt_brick import brick


class NxtNode(object):
    '''Robair nxt node'''
    def __init__(self, node_name="nxt_motion_control"):
        self.node_name = node_name
        rospy.init_node(self.node_name)
        rospy.Subscriber('/cmd', Command, self.new_cmd)
        self.current_cmd = Command(0, 0)
        self.motor_a = nxt.Motor(brick, nxt.PORT_A)
        self.motor_b = nxt.Motor(brick, nxt.PORT_B)

    def new_cmd(self, cmd):
        if cmd.speed is None:
            cmd.speed = self.current_cmd.speed
        self.current_cmd.speed = self.current_cmd.speed + cmd.speed
        if self.current_cmd.speed < 0:
            self.current_cmd.speed = -1
        elif self.current_cmd.speed > 0:
            self.current_cmd.speed = 1
        self.current_cmd.curve = cmd.curve

    def move(self, speed):
        if speed > 0:
            self.motor_a.run(power=65)
            self.motor_b.run(power=65)
        elif speed == 0:
            self.motor_a.idle()
            self.motor_b.idle()
        else:
            self.motor_a.run(power=-65)
            self.motor_b.run(power=-65)

    def turn(self, degrees):
        if degrees > 0:
            self.motor_a.turn(70, 100)
        elif degrees < 0:
            self.motor_b.turn()

    def main_loop(self):
        while not rospy.is_shutdown():
            speed, degrees = self.current_cmd.speed, self.current_cmd.curve
            if degrees > 0:
                if speed >= 0:
                    self.motor_a.turn(70, 100)
                else:
                    self.motor_b.turn(-70, 100)
            elif degrees < 0:
                if speed >= 0:
                    self.motor_b.turn(70, 100)
                else:
                    self.motor_a.turn(-70, 100)
            self.current_cmd.curve = 0
            self.move(speed)
            time.sleep(0.1)

if __name__ == '__main__':
    nxt_node = NxtNode()
    rospy.loginfo("%s running..." % nxt_node.node_name)
    nxt_node.main_loop()
    rospy.loginfo("%s stopped." % nxt_node.node_name)
