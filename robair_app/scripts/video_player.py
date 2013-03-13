#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from PySide.QtGui import QApplication
from PySide.phonon import Phonon

app = QApplication([])
app.setApplicationName('Phonon Video Player')

file_path = 'http://127.0.0.1:9090/'
media_src = Phonon.MediaSource(file_path)

media_obj = Phonon.MediaObject()

media_obj.setCurrentSource(media_src)

video_widget = Phonon.VideoWidget()

Phonon.createPath(media_obj, video_widget)

audio_out = Phonon.AudioOutput(Phonon.VideoCategory)
Phonon.createPath(media_obj, audio_out)

video_widget.show()

media_obj.play()

app.exec_()
