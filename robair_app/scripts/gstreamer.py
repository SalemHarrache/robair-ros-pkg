#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import subprocess
import argparse
from multiprocessing import Process
import socket


class GstreamerServer:

    def __init__(self, port_to_share, remote_host, remote_port=9999):
        self.port_to_share = port_to_share
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.server_worker = Process(target=self._shareWebcam)
        self.client_worker = Process(target=self._display)

# lance le partage de sa webcam sur le réseau, retourne son adresse IP
    def _shareWebcam(self):
        command = ('gst-launch v4l2src  ! decodebin ! queue ! ffmpegcolorspace'
                   '! x264enc byte-stream=true bitrate=200 bframes=4 ref=1 '
                   'me=dia subme=1 weightb=true threads=0 ! avimux ! '
                   'tcpserversink port=%d' % self.port_to_share)
        self.p_serv = subprocess.Popen(command, stdout=subprocess.PIPE,
                                       bufsize=-1, shell=True)
        info = socket.getaddrinfo(socket.gethostname(), None)
        print info
        return info

    def start_server(self):
        self.server_worker.start()

    def stop_server(self):
        self.server_worker.terminate()

    def wait_server(self):
        self.server_worker.join()

############################################################

    def _display:
        command = ('gst-launch v4l2src  ! decodebin ! queue ! ffmpegcolorspace'
                   '! x264enc byte-stream=true bitrate=200 bframes=4 ref=1 '
                   'me=dia subme=1 weightb=true threads=0 ! avimux ! '
                   'tcpclientsink port=%d' % self.remote_port)
        self.p_client = subprocess.Popen(command, stdout=subprocess.PIPE,
                                         bufsize=-1, shell=True)
        self.p_client.communicate()

    def start_client(self):
        self.client_worker.start()

    def stop_client(self):
        self.client_worker.terminate()

    def wait_client(self):
        self.client_worker.join()

if __name__ == "__main__":
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument('-port', type=int, default=9998)
        parser.add_argument('-rport', type=int, default=9999)
        parser.add_argument('-rhost', default="localhost")

        args = parser.parse_args()

        gstreamer_server = GstreamerServer(args.port, args.rport, args.rhost)
        gstreamer_server.start_server()
        print "fin "
        # gstreamer_server.wait_server()
