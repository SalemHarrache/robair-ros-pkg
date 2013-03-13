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
    return Response(video_stream_tcp(), mimetype='video/x264')


@app.before_first_request
def run_gstreamer():
    def gstreamer_task():

        command = ('gst-launch v4l2src  ! decodebin ! queue ! ffmpegcolorspace'
                   '! x264enc byte-stream=true bitrate=200 bframes=4 ref=1'
                   'me=dia subme=1 weightb=true threads=0 ! avimux ! '
                   'tcpserversink port=9999')
        subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=-1,
                         shell=True)
    gstreamer_worker = multiprocessing.Process(target=gstreamer_task)
    gstreamer_worker.start()


def video_stream_udp():
    buffer_size = 1000
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 9999))
    s.setblocking(0)
    while True:
        print("looping...")
        readable = select([s], [], [])
        yield readable[0][0].recv(buffer_size)


def video_stream_tcp():
    buffer_size = 100
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
