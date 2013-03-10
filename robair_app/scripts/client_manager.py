#!/usr/bin/env python
from __future__ import unicode_literals
import os
import roslib
import rospy

roslib.load_manifest('robair_app')

from robair_app.manager import ClientBot


if __name__ == '__main__':
    jid = rospy.get_param('tv_jabber_id')
    password = rospy.get_param('tv_jabber_password')

    node_name = os.path.basename(__file__).strip('.py')

    xmpp = ClientBot(jid, password, node_name)

    xmpp.connect()
    xmpp.process(block=False)
    rospy.loginfo("%s running..." % node_name)
    xmpp.send_message('robair@quicker.fr', 'Hello Robair!')
    rospy.spin()
    rospy.loginfo("%s stopping..." % node_name)
    xmpp.disconnect()

    rospy.loginfo("%s stopped." % node_name)
