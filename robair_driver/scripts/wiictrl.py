#!/usr/bin/env python
import roslib
import threading
import time
import sys
import rospy

from wiimote.wiimoteExceptions import *
from wiimote.wiimoteConstants import *
import wiimote.WIIMote
import wiimote.wiiutils

roslib.load_manifest('robair_driver')

from robair_msgs.msg import Command


class WiimoteNode():
    '''Robair wiimote node'''
    def __init__(self, node_name="wiimote"):
        self.node_name = node_name

    def runWiimoteNode(self):
        """Initialize the wiimote_node, establishing its name for communication with the Master"""

        # All exceptions will end up in the __main__ section
        # and are handled there:

        rospy.init_node('wiimote', anonymous=True, log_level=rospy.DEBUG) # log_level=rospy.DEBUG

        wiimoteDevice = wiimote.WIIMote.WIIMote()
        wiimoteDevice.zeroDevice()

        try:
            wiiPublisher = CmdSender(wiimoteDevice, freq=100)
            wiiPublisher.main_loop()
            #WiimoteListeners(wiimoteDevice).start()
        except:
            rospy.loginfo("Error in startup")
            rospy.loginfo(sys.exc_info()[0])
        finally:
            try:
                wiimoteDevice.setRumble(False)
                wiimoteDevice.setLEDs([False, False, False, False])
                wiimoteDevice.shutdown()
            except:
                pass

    def shutdown(self):
        try:
            #WiimoteListener.stop
            print "ciao !"
        except:
            pass
            
class CmdSender():#threading.Thread):
    """Broadcasting Wiimote accelerator and buttons readings as Command messages to Topic cmd"""
    
    def __init__(self, wiiMote, freq=10):
        
        """Initializes the Wiimote Command publisher.
    
        Parameters:
            wiiMote: a bluetooth-connected, calibrated WIIMote instance
            freq:    the message sending frequency in messages/sec. Max is 100, because
                     the Wiimote only samples the sensors at 100Hz.
        """
        
        #threading.Thread.__init__(self)
        self.wiiMote = wiiMote
        self.freq = freq
        self.sleepDuration = 1.0 / freq
        self.buttonCtrl=True
        
        self.pub = rospy.Publisher('cmd', Command)      
        
    def main_loop(self):
        """Loop that obtains the latest wiimote state, publishes the accelerator/buttons data and sleeps
        
        If button A is pressed, accelerometer is being used to publish command messages.
        You can come back to button control by pressing B
        
        Only X and Y Wiimote linear accelerator values are to be known. They remain in the [-10,10] interval.
        """
        
        rospy.loginfo("Wiimote cmd data publisher starting (topic /cmd).")
        #self.threadName = "Cmd topic Publisher"
        is_in = lambda x,y,z:x>y and x<z

        try:
            while not rospy.is_shutdown():
                self.wiistate = self.wiiMote.getWiimoteState()
    	        # Convert acceleration, which is in g's into m/sec^2:
                canonicalAccel=self.wiistate.acc.scale(EARTH_GRAVITY) 
                msg = Command(curve=None,
                          speed=None)       
                
                # If button B has been pressed use buttons (default)
                #  if A is pressed use accelerometer
                if self.wiistate.buttons[BTN_B]:
                    self.buttonCtrl=True
                if self.wiistate.buttons[BTN_A]:
                    self.buttonCtrl=False
                
                
                if buttonCtrl:
                    (msg.curve, msg.speed)=(0,0)
                    if self.wiistate.buttons[BTN_LEFT]:
                        msg.curve=1
                    elif self.wiistate.buttons[BTN_RIGHT]:
                        msg.curve=11
                    if self.wiistate.buttons[BTN_UP]:
                        msg.speed=1
                    if self.wiistate.buttons[BTN_DOWN]:
                        msg.speed=11
                else:
                    if is_in(abs(canonicalAccel[X]),0,2):
                        msg.curve=0
                    elif is_in(canonicalAccel[X],2,5):
                        msg.curve=1
                    elif is_in(canonicalAccel[X],5,8):
                        msg.curve=2
                    elif abs(canonicalAccel[X])>8:
                        msg.curve=3
                    if msg.curve > 0:
                        msf.curve+=10
    
                    if is_in(abs(canonicalAccel[Y]),0,2):
                        msg.speed=0
                    elif is_in(canonicalAccel[Y],2,5):
                        msg.speed=1
                    elif is_in(canonicalAccel[Y],5,8):
                        msg.speed=2
                    elif abs(canonicalAccel[Y])>8:
                        msg.speed=3
                    if msg.speed > 0:
                        msg.speed+=10
                
		try:
		  self.pub.publish(msg)
		except rospy.ROSException:
		  rospy.loginfo("Topic /cmd closed. Shutting down Imu sender.")
		  exit(0)
                
                rospy.sleep(self.sleepDuration)

        except rospy.ROSInterruptException:
            rospy.loginfo("Shutdown request. Shutting down Cmd sender.")
            exit(0)


class WiimoteListeners(threading.Thread):
    """Listen for request to rumble and LED blinking.
    """
    
    def __init__(self, wiiMote):
        
        threading.Thread.__init__(self)
        self.wiiMote = wiiMote    
        
        self.ledCommands = [False, False, False, False]
	self.rumbleCommand = False
        
        
    def run(self):
        

      def calibrateCallback(req):
        """The imu/calibrate service handler."""
          
        rospy.loginfo("Calibration request")
        
        calibrationSuccess = self.wiiMote.zeroDevice()
        self.is_CalibratedResponseMsg.data = calibrationSuccess
        
        return EmptyResponse()

      # Done with embedded function definitions. Back at the top
      # level of WiimoteListeners' run() function.
       
      try:
          rospy.spin()
      except rospy.ROSInterruptException:
        rospy.loginfo("Shutdown request. Shutting down Wiimote listeners.")
        exit(0)

if __name__ == '__main__':
    wiimoteNode = WiimoteNode()
    try:
        wiimoteNode.runWiimoteNode()
    except rospy.ROSInterruptException:
        rospy.loginfo("ROS Shutdown Request.")
    except KeyboardInterrupt, e:
        rospy.loginfo("Received keyboard interrupt.")
    except WiimoteNotFoundError, e:
        rospy.logfatal(str(e))
    except WiimoteEnableError, e:
        rospy.logfatal(str(e))
    except CallbackStackMultInstError, e:
        rospy.logfatal(str(e))
    except CallbackStackEmptyError, e:
        rospy.logfatal(str(e))
    except ResumeNonPausedError, e:
        rospy.logfatal(str(e))
    except CallbackStackEmptyError, e:
        rospy.logfatal(str(e))

    except:
        excType, excValue, excTraceback = sys.exc_info()[:3]
        traceback.print_exception(excType, excValue, excTraceback)
    finally:
        if (wiimoteNode is not None):
            wiimoteNode.shutdown()
        rospy.loginfo("Exiting Wiimote node.")
        sys.exit(0)


