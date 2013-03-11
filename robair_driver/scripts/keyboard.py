#!/usr/bin/env python
from __future__ import division
import sys
import roslib

roslib.load_manifest('robair_driver')

import rospy
from PySide import QtGui, QtCore

from robair_msgs.msg import Command


class KeyboardNode(QtGui.QWidget):
    '''Robair keyboard node'''
    def __init__(self, topic='/cmd'):
        super(QtGui.QWidget, self).__init__()
        self.pub = rospy.Publisher(topic, Command)
        rospy.init_node('keyboard')

    def keyPressEvent(self, event):
        directions = {QtCore.Qt.UpArrow: (1, 0),
                      QtCore.Qt.DownArrow: (-1, 0),
                      QtCore.Qt.LeftArrow: (4, 1),
                      QtCore.Qt.RightpArrow: (1, 90)}
        key = event.key()
        if key in directions.keys():
            msg = Command(*directions[key])
            self.pub.publish(msg)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    keyboard_node = KeyboardNode()
    sys.exit(app.exec_())
    keyboard_node.main_loop()
