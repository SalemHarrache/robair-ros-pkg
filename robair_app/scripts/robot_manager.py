#!/usr/bin/env python

from __future__ import division
import os
import roslib
import rospy

roslib.load_manifest('robair_app')

from robair_app.xmpp import RobBot


if __name__ == '__main__':
    node_name = os.path.basename(__file__).strip('.py')

    xmpp = RobBot(node_name)

    xmpp.connect()
    xmpp.process(block=False)
    rospy.loginfo("%s running..." % node_name)
    rospy.spin()
    rospy.loginfo("%s stopping..." % node_name)
    xmpp.disconnect()

    rospy.loginfo("%s stopped." % node_name)
