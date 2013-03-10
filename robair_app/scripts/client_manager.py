#!/usr/bin/env python

from __future__ import division
import os
import roslib
import rospy

roslib.load_manifest('robair_app')

from robair_app.xmpp import ClientBot


if __name__ == '__main__':
    jid = rospy.get_param('tv_jabber_id')
    password = rospy.get_param('tv_jabber_password')

    node_name = os.path.basename(__file__).strip('.py')

    xmpp_bot = ClientBot(node_name, jid, password)
    xmpp_bot.serve_forever()
    rospy.loginfo("%s running..." % node_name)
    rospy.spin()
    rospy.loginfo("%s stopped." % node_name)
