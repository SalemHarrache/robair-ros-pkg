#!/usr/bin/env python

from __future__ import division
import roslib
import subprocess

roslib.load_manifest('robair_driver')

import rospy
from std_msgs.msg import String


class WebcamNode():
    '''Robair battery node'''
    def __init__(self, topic='/info/image', pubrate=10):
        # TODO: publish image from gstreamer server to topic /info/image
        self.pub = rospy.Publisher(topic, String)
        rospy.init_node('webcam')

    def run_gstreamer(self):
        command = ('gst-launch v4l2src device=/dev/video0 ! '
                   '\'video/x-raw-yuv,width=640,height=480\' ! '
                   'x264enc pass=qual quantizer=20 tune=zerolatency ! avimux !'
                   ' tcpserversink  port=9999')

        subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         bufsize=-1,
                         shell=True)


if __name__ == '__main__':
    webcam_node = WebcamNode()
    webcam_node.run_gstreamer()
