# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from PySide import QtGui
from PySide.phonon import Phonon


def get_widget_player(file_path):
    media_src_rem = Phonon.MediaSource(file_path)
    media_obj_rem = Phonon.MediaObject()
    media_obj_rem.setCurrentSource(media_src_rem)
    video_widget = Phonon.VideoWidget()
    Phonon.createPath(media_obj_rem, video_widget)
    #audio_out = Phonon.AudioOutput(Phonon.VideoCategory)
    #Phonon.createPath(media_obj_rem, audio_out)
    return media_obj_rem, video_widget


class VideoStreamPlayer(object):
    def __init__(self, local_url, remote_url):
        self.app = QtGui.QApplication([])
        self.app.setApplicationName('Visio Video Player')
        self.frame = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()
        self.layout.columnMinimumWidth(11)
        self.local_media, self.local_widget = get_widget_player(local_url)
        self.remote_media, self.remote_widget = get_widget_player(remote_url)
        self.local_widget.setMaximumSize(200, 150)
        self.layout.addWidget(self.remote_widget, 0, 0, 10, 10)
        self.layout.addWidget(self.local_widget, 9, 9, 1, 1)

    def show(self):
        self.frame.setLayout(self.layout)
        self.frame.show()
        self.local_media.play()
        self.remote_media.play()
        self.app.exec_()
