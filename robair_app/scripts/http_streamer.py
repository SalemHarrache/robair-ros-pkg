#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import socket
import select
import uuid
import subprocess
import multiprocessing
from flask import Flask, Response

import roslib
import rospy

roslib.load_manifest('robair_app')

app = Flask(__name__)
app.secret_key = uuid.uuid4()


@app.route('/', methods=["GET"])
def video():
    return Response(video_stream_tcp(), mimetype='video/mp4')


def run_gstreamer():
    def gstreamer_task():
        device = rospy.get_param('webcam_device')
        command = ('gst-launch v4l2src device=%s ! '
                   '\'video/x-raw-yuv,width=640,height=480\' ! '
                   'x264enc pass=qual quantizer=20 tune=zerolatency ! avimux !'
                   ' tcpserversink  port=9999' % device)
        print
        subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=-1,
                         shell=True)
    gstreamer_worker = multiprocessing.Process(target=gstreamer_task)
    gstreamer_worker.start()
    return gstreamer_worker


def video_stream_tcp():
    buffer_size = 10000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('', 9999))
    while True:
        readable = select([s], [], [])
        yield readable[0][0].recv(buffer_size)


def run(node_name):
    rospy.init_node(node_name)
    gstreamer_worker = run_gstreamer()
    app.debug = False
    app.run(port=9090, threaded=True)
    gstreamer_worker.terminate()
    gstreamer_worker.join()

if __name__ == '__main__':
    node_name = os.path.basename(__file__).strip('.py')
    rospy.loginfo("%s running..." % node_name)
    run(node_name)
    rospy.loginfo("%s stopped." % node_name)
