#!/usr/bin/env python

from __future__ import division
import roslib
import subprocess
from multiprocessing import Process

roslib.load_manifest('robair_driver')

import rospy
from std_msgs.msg import String


class WebcamNode():
    '''Robair battery node'''
    def __init__(self, topic='/info/image', pubrate=10):
        # TODO: publish image from gstreamer server to topic /info/image
        self.pub = rospy.Publisher(topic, String)
        rospy.init_node('webcam')
        self.gstreamer_worker = Process(target=self._gstreamer_task)

    def start(self):
        self.gstreamer_worker.start()

    def stop(self):
        self.gstreamer_worker.terminate()
        self.gstreamer_worker.join()

    def _gstreamer_task(self):
        device = rospy.get_param('webcam_device', '/dev/video0')
        command = ('gst-launch v4l2src device=%s ! '
                   '\'video/x-raw-yuv,width=640,height=480\' ! '
                   'x264enc pass=cbr quantizer=20 tune=zerolatency ! avimux !'
                   ' tcpserversink  port=9999' % device)
        subprocess.call(command, shell=True, bufsize=-1)


if __name__ == '__main__':
    webcam_node = WebcamNode()
    rospy.loginfo("webcam running...")
    webcam_node.start()
    rospy.spin()
    webcam_node.stop()
    rospy.loginfo("webcam stopped.")
