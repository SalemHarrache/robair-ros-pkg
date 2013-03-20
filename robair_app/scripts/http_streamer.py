#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import socket
import select
import uuid
from flask import Flask, Response


app = Flask(__name__)
app.secret_key = uuid.uuid4()


@app.route('/', methods=["GET"])
def video():
    return Response(video_stream_tcp(), mimetype='video/mp4')


def video_stream_tcp():
    buffer_size = 10000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('', 9999))
    while True:
        readable = select.select([s], [], [])
        yield readable[0][0].recv(buffer_size)


def run():
    app.debug = False
    app.run(port=9090, host="0.0.0.0", threaded=True)

if __name__ == "__main__":
    run()
