#!/usr/bin/env python

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from pprint import pprint
import subprocess
import argparse

# URL list taken from http://blog.scoopz.com/2011/05/05/listen-to-any-bbc-radio-live-stream-using-vlc-including-radio-1-and-1xtra/
STATIONS = [
    ['OnePeace', 'http://midori.quicker.fr/InNuYWtlLWJpZ2Jvc3Mi.POHN0XlDCMH13fpejhHHYNaaiBQ/files/Animes/onepiece/last/One_Piece_585_SD_Impel-Down.mp4'],
 ]
WIN_TITLE = "clientTV"

class Win(QMainWindow):
    def __init__(self, parent=None):
        super(Win, self).__init__(parent)
        self.player = None
        # args
        parser = argparse.ArgumentParser(description='BBC radio player')
        parser.add_argument('-p', '--player', default='vlc')
        parser.add_argument('player_args', nargs='*')
        args = parser.parse_args()
        self.player_prog = args.player
        self.player_args = args.player_args
        # UI
        self.setWindowTitle(WIN_TITLE)
        self.setMinimumSize(300, 600)
        self.scroll_area = QScrollArea()
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.widget)
        self.setCentralWidget(self.scroll_area)
        for name, url in STATIONS:
            button = QPushButton(name.replace('&', '&&'))
            button.args = {
                'name': name,
                'url': url,
            }
            button.clicked.connect(self.listen)
            self.layout.addWidget(button)
        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_player)

    def listen(self):
        pressed_button = self.sender()
        for button in self.widget.findChildren(QPushButton):
            if button != pressed_button and not button.isEnabled():
                button.setEnabled(True)
                break
        pressed_button.setEnabled(False)
        # stop the running player instance before starting another one
        if self.player:
            if self.player.poll() is None:
                self.player.terminate()
                self.player.wait()
        cmd = [self.player_prog]
        cmd.extend(self.player_args)
        cmd.append(pressed_button.args['url'])
        try:
            self.player = subprocess.Popen(cmd)
        except Exception, e:
            msg_box = QMessageBox()
            msg_box.setText('Couldn\'t launch\n"%s"' % ' '.join(cmd))
            msg_box.setInformativeText(unicode(e))
            msg_box.exec_()
            pressed_button.setEnabled(True)
        self.setWindowTitle('%s - %s' % (pressed_button.args['name'], WIN_TITLE))
        self.timer.start(200)

    def check_player(self):
        if self.player and self.player.poll() is not None:
            # the player has been stopped
            self.player = None
            self.timer.stop()
            self.setWindowTitle(WIN_TITLE)
            for button in self.widget.findChildren(QPushButton):
                if not button.isEnabled():
                    button.setEnabled(True)
                    break


# if __name__ == '__main__':
app = QApplication(sys.argv)
win = Win()
win.show()
sys.exit(app.exec_())

