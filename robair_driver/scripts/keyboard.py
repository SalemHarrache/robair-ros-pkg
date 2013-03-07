#!/usr/bin/env python

from __future__ import division
import roslib

roslib.load_manifest('robair_driver')

import rospy
import sys
from PySide import QtGui, QtCore

from std_msgs.msg import String
from robair_msgs.msg import Command

class KeyboardNode(QtGui.QWidget):
    '''Robair keyboard node'''
    def __init__(self, topic='/cmd', pubrate=10):
        self.pub = rospy.Publisher(topic, String)
        rospy.init_node('keyboard')
        # fake keyboard states generator


    def keyPressEvent(self, e):
        
    msg=Commande()
    key = event.key()
    if key == QtCore.Qt.UpArrow
	msg.speed=1
	msg.angle=0
        self.pub.publish(self.msg)
    if key == QtCore.Qt.DownArrow:
	msg.speed=-1
	msg.angle=0
        self.pub.publish(self.msg)
    if key == QtCore.Qt.LeftArrow
	msg.speed=4
	msg.angle=1
        self.pub.publish(self.msg)
    if key == QtCore.Qt.RightpArrow
	msg.speed=1
	msg.angle=90
        self.pub.publish(self.msg)


    def keyReleaseEvent(self, e):

    msg=Commande()
    key = event.key()
    if key == QtCore.Qt.UpArrow
	msg.speed=1
	msg.angle=90
        self.pub.publish(self.msg)
    if key == QtCore.Qt.DownArrow:
	msg.speed=1
	msg.angle=90
        self.pub.publish(self.msg)
    if key == QtCore.Qt.LeftArrow
	msg.speed=1
	msg.angle=90
        self.pub.publish(self.msg)
    if key == QtCore.Qt.RightpArrow
	msg.speed=1
	msg.angle=90
        self.pub.publish(self.msg)



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
    keyboard_node = Node()
    keyboard_node.main_loop()
