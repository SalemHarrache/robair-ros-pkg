#!/usr/bin/env python
from __future__ import unicode_literals
import os
import roslib
import rospy

roslib.load_manifest('robair_app')

from robair_app.manager import ClientManager


if __name__ == '__main__':
    node_name = os.path.basename(__file__).strip('.py')
    xmpp = ClientManager(node_name)
    # first test > \o/
    assert xmpp.proxy_robot.add(-5, 3, 3) == 1

    rospy.loginfo("%s running..." % node_name)
    rospy.spin()
    rospy.loginfo("%s stopping..." % node_name)
    xmpp.disconnect()
    rospy.loginfo("%s stopped." % node_name)
