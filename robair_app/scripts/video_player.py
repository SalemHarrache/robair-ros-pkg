#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from PySide import QtGui
from PySide.phonon import Phonon
import multiprocessing


def get_widget_player(file_path):
    media_src_rem = Phonon.MediaSource(file_path)
    media_obj_rem = Phonon.MediaObject()
    media_obj_rem.setCurrentSource(media_src_rem)
    video_widget = Phonon.VideoWidget()
    Phonon.createPath(media_obj_rem, video_widget)
    audio_out = Phonon.AudioOutput(Phonon.VideoCategory)
    Phonon.createPath(media_obj_rem, audio_out)
    media_obj_rem.play()
    return video_widget


class VideoStreamPlayer(object):
    def __init__(self, local_url, remote_url):
        self.app = QtGui.QApplication([])
        self.app.setApplicationName('Visio Video Player')
        self.frame = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()

        self.layout.addWidget(get_widget_player(local_url), 0, 0, 10, 10)
        self.layout.addWidget(get_widget_player(remote_url), 0, 0, 10, 10)

        self.process = multiprocessing.Process(target=self.app.exec_)

    def show(self):
        self.frame.show()
        self.frame.setLayout(self.layout)
        self.process.start()

    def dispose(self):
        self.process.terminate()
        self.process.join()


app = VideoStreamPlayer("http://127.0.0.1:9090/", "http://127.0.0.1:9090/")
app.show()
