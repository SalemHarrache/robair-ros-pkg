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


@app.route('/webcam.ogg', methods=["GET"])
def video():
    return Response(video_stream(), mimetype='video/ogg')


def video_stream():
    def run_gstreamer():
        command = ('gst-launch-0.10 videotestsrc ! queue ! videorate '
                   ' ! "video/x-raw-yuv,width=640,'
                   'height=480,framerate=15/1" ! queue ! theoraenc '
                   'quality=15 ! queue ! muxout. pulsesrc ! audio/x-'
                   'raw-int,rate=22000,channels=1,width=16 ! queue '
                   '! audioconvert ! vorbisenc ! queue ! muxout. '
                   'oggmux name=muxout ! tcpserversink port=9999')
        subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=-1,
                         shell=True)
    gstreamer_worker = multiprocessing.Process(target=run_gstreamer)
    gstreamer_worker.start()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('', 9999))
    while True:
        readable = select([s], [], [], 0.1)[0]
        for s in readable:
            data = s.recv(10000)
            if not data:
                break
            yield data
    gstreamer_worker.terminate()
    gstreamer_worker.join()


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
