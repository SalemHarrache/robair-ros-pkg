# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from PySide import QtGui
from PySide.phonon import Phonon


def get_widget_player(file_path, audio):
    media_src = Phonon.MediaSource(file_path)
    media_obj = Phonon.MediaObject()
    media_obj.setCurrentSource(media_src)
    video_widget = Phonon.VideoWidget()
    Phonon.createPath(media_obj, video_widget)
    if audio:
        audio_out = Phonon.AudioOutput(Phonon.VideoCategory)
        Phonon.createPath(media_obj, audio_out)
    return media_obj, video_widget


class VideoStreamPlayer(object):
    def __init__(self, local_url, remote_url):
        self.app = QtGui.QApplication([])
        self.app.setApplicationName('Visio Video Player')
        self.frame = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()
        self.layout.columnMinimumWidth(11)
        self.local_media, self.local_widget = get_widget_player(local_url,
                                                                False)
        self.remote_media, self.remote_widget = get_widget_player(remote_url,
                                                                  True)
        self.local_widget.setMaximumSize(200, 150)
        self.layout.addWidget(self.remote_widget, 0, 0, 10, 10)
        self.layout.addWidget(self.local_widget, 9, 9, 1, 1)

    def show(self):
        self.frame.setLayout(self.layout)
        self.frame.show()
        self.local_media.play()
        self.remote_media.play()
        self.app.exec_()

if __name__ == "__main__":
    pom = VideoStreamPlayer('http://127.0.0.1:9090', 'http://127.0.0.1:9090')
    pom.show()
