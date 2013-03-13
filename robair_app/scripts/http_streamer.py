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
    return Response(video_stream_udp(), mimetype='video/mp4')


@app.before_first_request
def run_gstreamer():
    def gstreamer_task():
        # command = ('gst-launch v4l2src  ! decodebin ! queue ! ffmpegcolorspace'
        #            '! x264enc byte-stream=true bitrate=200 bframes=4 ref=1 '
        #            'me=dia subme=1 weightb=true threads=0 ! avimux ! '
        #            'tcpserversink port=9999 ')

        command = ('gst-launch -v v4l2src device=/dev/video0 ! \'video/x-raw-yuv,'
                   'width=640,height=480\' !  x264enc pass=qual quantizer=20 '
                   'tune=zerolatency ! rtph264pay ! udpsink host=127.0.0.1'
                   'port=9999')

        # x264enc bitrate=500 speed-preset=superfast ! rtph264pay ! udpsink host=244.1.1.1 port=5000 auto-multicast=true
        # x264enc byte-stream=true bitrate=200 bframes=4 ref=1 ' 'me=dia subme=1 weightb=true threads=0
        subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=-1,
                         shell=True)
    gstreamer_worker = multiprocessing.Process(target=gstreamer_task)
    gstreamer_worker.start()
    # socket_Serv
    address = ('localhost', 9999)
    server_socket = socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(address)
    while(1):
        recv_data, addr = server_socket.recvfrom(2048)
        print "We got a client "
        print recv_data
        if recv_data == 'I_wanna_see_you':
            #boucle sur udpsink mais je ne sais pas comment on fait
            server_socket.sendto("videooo", addr)


def video_stream_udp():
    buffer_size = 1000
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = ('localhost', 9999)

    client_socket.sendto('I_wanna_see_you', address)

    client_socket.setblocking(0)
    while True:
        print("looping...")
        recv_data, addr = client_socket.recvfrom(2048)
        readable = select([client_socket], [], [])
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
