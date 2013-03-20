#!/usr/bin/env python

from __future__ import division
import roslib

roslib.load_manifest('robair_driver')

import rospy
from std_msgs.msg import String


class BatteryNode():
    '''Robair battery node'''
    def __init__(self, topic='/info/battery_level', pubrate=1):
        self.pub = rospy.Publisher(topic, String)
        rospy.init_node('battery')
        # fake battery states generator
        self.state_gen = ('%.2f' % (100 - (i / 100)) for i in xrange(1, 100))
        self.time_sleep = 1 / pubrate if pubrate != 0 else 1

    @property
    def level(self):
        try:
            return self.state_gen.next()
        except:
            return 0

    def main_loop(self):
        while not rospy.is_shutdown():
            self.pub.publish(self.level)
            rospy.sleep(self.time_sleep)


if __name__ == '__main__':
    battery_node = BatteryNode()
    battery_node.main_loop()
