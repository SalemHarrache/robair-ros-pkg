#!/usr/bin/env python
import roslib
import cwiid
import sys

roslib.load_manifest('robair_driver')

import rospy

from robair_msgs.msg import Command
from robair_driver import keylogger


class WiimoteNode(threading.Thread):
    '''Robair wiimote node'''
    def __init__(self, topic='/cmd', node_name="wiimote", freq=100, wiimote_addr='00:1C:BE:F7:64:04'):
        threading.Thread.__init__(self)
        self.freq = freq
        self.sleepDuration = 1.0 / freq
        self.node_name = node_name
        self.pub = rospy.Publisher(topic, Command)
        self.wiimote_addr=wiimote_addr
        rospy.init_node('wiimote')

    def main_loop(self, direction, speed):

	done = lambda: rospy.is_shutdown()
        print 'Press buttons 1 + 2 on your Wii Remote...'
        time.sleep(1)

        print 'Put Wiimote in discoverable mode now (press 1+2)...'
        if self.wiimote_addr != 0:
            wm = cwiid.Wiimote(self.wiimote_addr)
        else:
            wm = cwiid.Wiimote()
    
	print 'Wii Remote connected...'
	print '\nPress the PLUS button to disconnect the Wiimote and end the application'
        time.sleep(1)
	
	Rumble = False
        wm.rpt_mode = cwiid.RPT_BTN
	
        while not done:
            if wm.state['buttons'] == 512:
                self.pub.publish(1,None)

            if wm.state['buttons'] == 256:
		self.pub.publish(-1,None)

	    if wm.state['buttons'] == 2048:
		self.pub.publish(None, -1)

	    if wm.state['buttons'] == 1024:
		self.pub.publish(None, 1)

	    if wm.state['buttons'] == 4096:
		print 'closing Bluetooth connection. Good Bye!'
		time.sleep(1)
		exit(wm)

            rospy.sleep(self.sleepDuration)

        wm.close()
    

if __name__ == '__main__':
    wiimote_node = WiimoteNode()
    rospy.loginfo("%s running..." % wiimote_node.node_name)
    wiimote_node.main_loop()
    rospy.loginfo("%s stopped." % wiimote_node.node_name)


