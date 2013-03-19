#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import socket
from select import select
import subprocess
import multiprocessing
from flask import Flask, Response


app = Flask(__name__)
app.secret_key = 'blablabla'


@app.route('/', methods=["GET"])
def video():
    return Response(video_stream_tcp(), mimetype='video/mp4')


@app.before_first_request
def run_gstreamer():
    def gstreamer_task():
        command = ('gst-launch v4l2src device=/dev/video0 ! '
                   '\'video/x-raw-yuv,width=640,height=480\' ! '
                   'x264enc pass=qual quantizer=20 tune=zerolatency ! avimux !'
                   ' tcpserversink  port=9999')

        subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=-1,
                         shell=True)
    gstreamer_worker = multiprocessing.Process(target=gstreamer_task)
    gstreamer_worker.start()


def video_stream_tcp():
    buffer_size = 10000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('', 9999))
    while True:
        readable = select([s], [], [])
        yield readable[0][0].recv(buffer_size)


def run():
    app.debug = False
    app.run(port=9090, threaded=True)


server = multiprocessing.Process(target=run)


if __name__ == "__main__":
    try:
        print 'Httpd serve forever'
        server.start()
    except KeyboardInterrupt:
        # server.terminate()
        server.join()
        print "Shutdown camera server ..."
