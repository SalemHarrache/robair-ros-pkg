#!/usr/bin/python
import subprocess
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler


class RequestHandler(BaseHTTPRequestHandler):
    def _writeheaders(self):
        self.send_response(200)
        self.send_header('Content-type', 'video/ogg')
        self.end_headers()

    def do_HEAD(self):
        self._writeheaders()

    def do_GET(self):
        self._writeheaders()
        DataChunkSize = 10000
        command = ("gst-launch-0.10 v4l2src ! tee name=videoout ! queue !"
                   " videorate ! 'video/x-raw-yuv,width=640,height=480,"
                   "framerate=30/1' ! queue ! theoraenc quality=60 ! "
                   "queue ! muxout. pulsesrc ! audio/x-raw-int,rate="
                   "22000,channels=1,width=16 ! queue ! audioconvert"
                   " ! vorbisenc ! queue ! muxout. oggmux name=muxout"
                   " ! filesink location=/dev/stdout videoout.")

        print("running command: %s" % (command, ))
        p = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=-1,
                             shell=True)
        print("starting polling loop.")
        while(p.poll() is None):
            print "looping... "
            stdoutdata = p.stdout.read(DataChunkSize)
            self.wfile.write(stdoutdata)
        print("Done Looping")
        print("dumping last data, if any")
        stdoutdata = p.stdout.read(DataChunkSize)
        self.wfile.write(stdoutdata)


if __name__ == '__main__':
    serveraddr = ('127.0.0.1', 9090)
    print 'Httpd serve forever on http://%s:%s' % serveraddr
    srvr = HTTPServer(serveraddr, RequestHandler)
    srvr.serve_forever()
