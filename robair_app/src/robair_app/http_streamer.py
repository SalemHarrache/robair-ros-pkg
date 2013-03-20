# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import socket
import select
import uuid
import multiprocessing

# from gevent.pywsgi import WSGIServer
from flask import Flask, Response
from .player import VideoStreamPlayer


def get_local_ip_address():
    ipaddr = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("google.fr", 80))
        ipaddr = s.getsockname()[0]
        s.close()
    except:
        pass
    return ipaddr


class HTTPStreamer(object):
    def __init__(self, debug=False, port=9090, host='0.0.0.0'):
        app = Flask(__name__)
        app.secret_key = uuid.uuid4()
        self.port = port
        self.host = host
        self.local_address = get_local_ip_address()
        app.debug = debug
        app.add_url_rule('/', 'webcam', self.video_stream_response)
        # self.wsgi = WSGIServer((self.host, self.port), app)
        # run_funct = lambda: self.wsgi.serve_forever()
        run_funct = lambda: app.run(port=self.port, host=self.host,
                                    threaded=True)
        self.server = multiprocessing.Process(target=run_funct)

    def video_stream_response(self):
        def video_stream_tcp():
            buffer_size = 10000
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('', 9999))
            while True:
                try:
                    readable = select.select([s], [], [])
                    yield readable[0][0].recv(buffer_size)
                except:
                    pass
        return Response(video_stream_tcp(), mimetype='video/mp4')

    @property
    def url(self):
        # this is the small hack for using local network ip address
        return "http://%s:%s/" % (self.host, self.port)

    def display(self, remote_host):
        player = VideoStreamPlayer(self.url, remote_host)
        process = multiprocessing.Process(target=player.show)
        process.start()
        process.join()

    def start(self):
        self.server.start()

    def stop(self):
        self.server.terminate()
        self.server.join()
