#!/usr/bin/env python

from __future__ import division
import roslib
import rospy

roslib.load_manifest('robair_app')

from robair_app.xmpp import RobBot


if __name__ == '__main__':
    jid = rospy.get_param('robot_jabber_id')
    password = rospy.get_param('robot_jabber_password')

    xmpp = RobBot(jid, password)
    xmpp.connect()
    xmpp.process(block=False)
    rospy.loginfo("robair_manager running...")
    rospy.spin()
    rospy.loginfo("robair_manager stopping...")
    xmpp.disconnect()

    rospy.loginfo("robair_manager stopped.")
