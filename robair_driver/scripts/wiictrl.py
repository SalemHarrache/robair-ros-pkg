#!/usr/bin/env python
import roslib
import cwiid
import threading
import rospy

roslib.load_manifest('robair_driver')


from robair_msgs.msg import Command


class WiimoteNode(threading.Thread):
    '''Robair wiimote node'''
    def __init__(self, topic='/cmd', node_name="wiimote", freq=4):
        threading.Thread.__init__(self)
        self.freq = freq
        self.button_ctrl = True
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
            rospy.sleep(1)

    def main_loop(self):
        print 'Put Wiimote in discoverable mode now (press 1+2)...'
        self.wm = self.get_wiimote()
        if self.wm is not None:
            print 'Wii Remote connected...'
            print '\nPress the HOME button to disconnect the Wiimote'
            rospy.sleep(1)

            self.wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC
            speed_x = 0
            speed_y = 0

            while not rospy.is_shutdown():

                if self.wm.state['buttons'] & cwiid.BTN_HOME:
                    print 'closing Bluetooth connection. Good Bye!'
                    return

                if self.wm.state['buttons'] & cwiid.BTN_A:
                    self.button_ctrl = True
                if self.wm.state['buttons'] & cwiid.BTN_B:
                    self.button_ctrl = False
                m_speed_x = speed_x
                m_speed_y = speed_y

                if self.button_ctrl:
                    if self.wm.state['buttons'] & cwiid.BTN_UP:
                        #if speed_x != 1:
                        speed_x = 1
                    if self.wm.state['buttons'] & cwiid.BTN_DOWN:
                        #if speed_x != -1:
                        speed_x = -1
                    if self.wm.state['buttons'] & cwiid.BTN_LEFT:
                        #if speed_y != -90:
                        speed_y = -90
                    if self.wm.state['buttons'] & cwiid.BTN_RIGHT:
                        #if speed_y != 90:
                        speed_y = 90
                else:
                    if self.wm.state['acc'][2] < 120:
                        speed_x = -1
                    if self.wm.state['acc'][2] > 130:
                        speed_x = 1
                    if self.wm.state['acc'][1] < 120:
                        speed_y = 90
                    if self.wm.state['acc'][1] > 130:
                        speed_y = -90

                if speed_x == m_speed_x:
                    speed_x = 0
                if speed_y == m_speed_y:
                    speed_y = 0
                if speed_x != 0 or speed_y != 0:
                    self.pub.publish(Command(speed_x, speed_y))
                rospy.sleep(self.sleepDuration)

    def shutdown(self):
        if self.wm is not None:
            self.wm.close()


if __name__ == '__main__':
    wiimote_node = WiimoteNode()
    rospy.loginfo("%s running..." % wiimote_node.node_name)
    wiimote_node.main_loop()
    rospy.spin()
    wiimote_node.shutdown()
    rospy.loginfo("%s stopped." % wiimote_node.node_name)
