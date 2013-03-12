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


def video_stream():
    pubsub = red.pubsub()
    pubsub.subscribe('video')
    for message in pubsub.listen():
        print "new_data"
        yield message['data']


@app.route('/webcam.ogg', methods=["GET"])
def video():
    return Response(video_stream(), mimetype='video/ogg')


# @app.before_first_request
def start_grab_video_task():
    def grab_video_task():
        command = ('gst-launch videotestsrc ! video/x-raw-rgb,framerate=5/1 '
                   '! ffmpegcolorspace ! vp8enc ! queue2 ! mux. audiotestsrc '
                   '! audioconvert ! audioresample ! vorbisenc ! queue2 '
                   '! mux. webmmux name=mux streamable=true '
                   '! filesink location=/dev/stdout')
        print("running command: %s" % command)
        p = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=-1,
                             shell=True)
        print("starting polling loop.")
        while(p.poll() is None):
            print "looping... "
            red.publish('video', p.stdout.read(1024))
        print "end looping..."
    worker = multiprocessing.Process(target=grab_video_task)
    worker.start()


def run():
    start_grab_video_task()
    app.debug = True
    app.run(port=9090)


server = multiprocessing.Process(target=run)


if __name__ == "__main__":
    server.start()
    # server.terminate()
    # server.join()
