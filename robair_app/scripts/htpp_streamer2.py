#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import redis
import subprocess
import multiprocessing
from flask import Flask, Response


red = redis.StrictRedis()
app = Flask(__name__)
app.secret_key = 'blablabla'


@app.route('/webcam.webm', methods=["GET"])
def video():
    return Response(video_stream(), mimetype='video/webm')


def video_stream():
    command = ('gst-launch videotestsrc ! tee name=videoout ! video/x-raw-rgb,framerate=5/1 '
               '! ffmpegcolorspace ! vp8enc ! queue2 ! mux. audiotestsrc '
               '! audioconvert ! audioresample ! vorbisenc ! queue2 '
               '! mux. webmmux name=mux streamable=true '
               '! filesink location=/dev/stdout videoout.')
    print("running command: %s" % command)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=-1,
                         shell=True)
    print("starting polling loop.")
    while p.poll() is None:
        print "looping... "
        yield p.stdout.read(10000)


def run():
    app.debug = True
    app.run(port=9090)


server = multiprocessing.Process(target=run)


if __name__ == "__main__":
    server.start()
    # server.terminate()
    # server.join()
