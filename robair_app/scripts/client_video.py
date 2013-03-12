import os
from PySide.QtGui import QApplication
from PySide.phonon import Phonon

app = QApplication([])
app.setApplicationName('Phonon Video Player')

#file_path = os.path.join(os.path.dirname(__file__), '320x240.ogv')

file_path = 'http://midori.quicker.fr/InNuYWtlLWJpZ2Jvc3Mi.POHN0XlDCMH13fpejhHHYNaaiBQ/files/Animes/onepiece/last/One_Piece_585_SD_Impel-Down.mp4'
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
