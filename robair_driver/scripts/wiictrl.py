#!/usr/bin/env python
import roslib
import cwiid
import threading
import time
import rospy

roslib.load_manifest('robair_driver')


from robair_msgs.msg import Command


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

    def get_wiimote(self):
        while not rospy.is_shutdown():
            try:
                return cwiid.Wiimote()
            except:
                pass
                time.sleep(1)

    def main_loop(self):
        print 'Put Wiimote in discoverable mode now (press 1+2)...'
        wm = self.get_wiimote()
        if wm is not None:
            print 'Wii Remote connected...'
            print '\nPress the HOME button to disconnect the Wiimote and stop the node'
            time.sleep(1)

            Rumble = False
            wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC
            speedX = 0
            speedY = 0
            is_in = lambda x, y, z: x > y and x <= z

            while not rospy.is_shutdown():

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
                        #if speedX != 1:
                        speedX = 1
                    if wm.state['buttons'] & cwiid.BTN_DOWN:
                        #if speedX != -1:
                        speedX = -1
                    if wm.state['buttons'] & cwiid.BTN_LEFT:
                        #if speedY != -90:
                        speedY = -90
                    if wm.state['buttons'] & cwiid.BTN_RIGHT:
                        #if speedY != 90:
                        speedY = 90
                else:
                    if wm.state['acc'][2] < 120:
                        speedX=-1
                    if wm.state['acc'][2] > 130:
                        speedX=1
                    if wm.state['acc'][1] < 120:
                        speedY=90
                    if wm.state['acc'][1] > 130:
                        speedY=-90

    #                wiiX=abs(wm.state['acc'][0] - 125)
    #                #if is_in(wiiX,0,6):
    #                    #speedX=0
    #                if is_in(wiiX,6,12):
    #                    speedX=1
    #                elif is_in(wiiX,12,18):
    #                    speedX=1#2
    #                elif wiiX > 18:
    #                    speedX=1#3
    #                if wm.state['acc'][0]<120:
    #                    speedX=-speedX
    #
    #                wiiY=abs(wm.state['acc'][1] - 125)
    #                #if is_in(wiiY,0,6):
    #                    #speedY=0
    #                if is_in(wiiY,6,12):
    #                    speedY=30
    #                elif is_in(wiiY,12,18):
    #                    speedY=60
    #                elif wiiY > 18:
    #                    speedY=90
    #                if wm.state['acc'][1] > 130:
    #                    speedY=-speedY

                if speedX == m_speedX:
                    speedX = 0
                if speedY == m_speedY:
                    speedY = 0
                if speedX != 0 or speedY != 0 :
                    self.pub.publish(Command(speedX, speedY))
                rospy.sleep(self.sleepDuration)

            wm.close()


if __name__ == '__main__':
    wiimoteNode = WiimoteNode()
    wiimoteNode.main_loop()


