#!/usr/bin/env python
import roslib
import cwiid
import sys
import threading
import time

roslib.load_manifest('robair_driver')

import rospy

from robair_msgs.msg import Command
from robair_driver import keylogger


class WiimoteNode(threading.Thread):
    '''Robair wiimote node'''
    def __init__(self, topic='/cmd', node_name="wiimote", freq=4):
        threading.Thread.__init__(self)
        self.freq = freq
        self.buttonCtrl = True
        self.sleepDuration = 1.0 / freq
        self.node_name = node_name
        self.pub = rospy.Publisher(topic, Command)
        rospy.init_node('wiimote')

    def main_loop(self):

	done = lambda: rospy.is_shutdown()

        print 'Put Wiimote in discoverable mode now (press 1+2)...'
        wm = cwiid.Wiimote()
	print 'Wii Remote connected...'
	print '\nPress the HOME button to disconnect the Wiimote and stop the node'
        time.sleep(1)
	
	Rumble = False
        wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC
        speedX=0
        speedY=0
        is_in = lambda x,y,z:x>y and x<=z

        while True:
            
	    if wm.state['buttons'] & cwiid.BTN_HOME:
		print 'closing Bluetooth connection. Good Bye!'
		time.sleep(1)
		exit(wm)

            if wm.state['buttons'] & cwiid.BTN_A:
                self.buttonCtrl=True
            if wm.state['buttons'] & cwiid.BTN_B:
                self.buttonCtrl=False
            m_speedX=speedX
            m_speedY=speedY

            if self.buttonCtrl:
                if wm.state['buttons'] & cwiid.BTN_UP:
                    if speedX != 3:
                       speedX += 1
                if wm.state['buttons'] & cwiid.BTN_DOWN:
                    if speedX != -3:
                        speedX -= 1
                if wm.state['buttons'] & cwiid.BTN_LEFT:
                    if speedY != -90:
                        speedY-= 30
                if wm.state['buttons'] & cwiid.BTN_RIGHT:
                    if speedY != 90:
                        speedY += 30
            else:
                wiiX=abs(wm.state['acc'][1] - 126)
                if is_in(wiiX,0,6):
                    speedX=0
                elif is_in(wiiX,6,12):
                    speedX=1
                elif is_in(wiiX,12,18):
                    speedX=2
                elif wiiX > 18:
                    speedX=3
                if wm.state['acc'][1]>120:
                    speedX=-speedX

                wiiY=abs(wm.state['acc'][0] - 125)
                if is_in(wiiY,0,6):
                    speedY=0
                elif is_in(wiiY,6,12):
                    speedY=30
                elif is_in(wiiY,12,18):
                    speedY=60
                elif wiiY > 18:
                    speedY=90
                if wm.state['acc'][0]<120:
                    speedY=-speedY

            if speedX != m_speedX or speedY != m_speedY :
                self.pub.publish(Command(speedX, speedY))
            rospy.sleep(self.sleepDuration)

        wm.close()
    

if __name__ == '__main__':
    wiimote_node = WiimoteNode()
    rospy.loginfo("%s running..." % wiimote_node.node_name)
    wiimote_node.main_loop()
    rospy.loginfo("%s stopped." % wiimote_node.node_name)


