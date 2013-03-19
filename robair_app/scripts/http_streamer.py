#!/usr/bin/env python
from __future__ import unicode_literals
import os
import roslib
import rospy

roslib.load_manifest('robair_app')

from robair_app.http_streamer import HTTPStreamer


if __name__ == '__main__':
    node_name = os.path.basename(__file__).strip('.py')

    server = HTTPStreamer()
    server.start()
    server.display(server.url)

    rospy.loginfo("%s running..." % node_name)
    rospy.spin()
    rospy.loginfo("%s stopping..." % node_name)
    server.stop()
    rospy.loginfo("%s stopped." % node_name)
