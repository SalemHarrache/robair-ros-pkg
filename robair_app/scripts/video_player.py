#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from PySide import QtGui
from PySide.phonon import Phonon

#! /usr/bin/python
#-*-coding: utf-8 -*-
from PySide.QtGui import *
from PySide.QtCore import *
import os,sys

def main(args):
    a = QApplication([])
    a.setApplicationName('Visio Video Player')
    fenetre = QWidget()

    bouton2 = QPushButton("textComment")
    bouton3 = QPushButton("notrewebcam")

    monLayout = QGridLayout()

    #####################"VIDEO1####################################"
    file_path = 'http://127.0.0.1:9090/'
    media_src_rem = Phonon.MediaSource(file_path)
    media_obj_rem = Phonon.MediaObject()
    media_obj_rem.setCurrentSource(media_src_rem)

    remote_video_widget = Phonon.VideoWidget()
    Phonon.createPath(media_obj_rem, remote_video_widget)

    audio_out = Phonon.AudioOutput(Phonon.VideoCategory)
    Phonon.createPath(media_obj_rem, audio_out)


    #####################"VIDEO2####################################"
    media_src = Phonon.MediaSource(file_path)
    media_obj_loc = Phonon.MediaObject()
    media_obj_loc.setCurrentSource(media_src)

    video_widget = Phonon.VideoWidget()
    Phonon.createPath(media_obj_loc, video_widget)
    video_widget.resize(50,50)
    # audio_out = Phonon.AudioOutput(Phonon.VideoCategory)
    # Phonon.createPath(media_obj_loc, audio_out)

    #########################################################"

    monLayout.addWidget(remote_video_widget,0,0,10,10)

    #monLayout.addWidget(bouton2,0,4,1,1)
    monLayout.addWidget(video_widget,0,0,1,1)




    fenetre.setLayout(monLayout)
    fenetre.show()

    media_obj_rem.play() #   VIDEO1
    media_obj_loc.play() #   VIDEO2
    r=a.exec_()
    return r
if __name__=="__main__":
    main(sys.argv)









# app = QApplication([])
# app.setApplicationName('Visio Video Player')

# monLayout = QHBoxLayout()


# file_path = 'http://127.0.0.1:9090/'
# media_src = Phonon.MediaSource(file_path)
# media_obj = Phonon.MediaObject()
# media_obj.setCurrentSource(media_src)

# remote_video_widget = Phonon.VideoWidget()
# Phonon.createPath(media_obj, remote_video_widget)

# audio_out = Phonon.AudioOutput(Phonon.VideoCategory)
# Phonon.createPath(media_obj, audio_out)

# monLayout.addWidget(remote_video_widget)

# remote_video_widget.show()
# media_obj.play()

# app.exec_()
