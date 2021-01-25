from multiprocessing import Process
import http.server
import socketserver
import signal, sys, getopt, time, subprocess, shlex, os, shutil, re


class quietHTTP(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class OriginService():

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr


    def serv_stream(self):
        strm_port = self.fhdhr.config.dict["origin"]["stream_port"]
        www_dir = os.path.abspath(os.getcwd()) + '/origin/www_dir'
        try:    # Make serving directory, if it does not exist
            os.mkdir(str(www_dir))
        except OSError:
            pass
        # Move to serving directory
        os.chdir(str(www_dir))
        # Start webserver
        print("Starting Stream Server on port:" + str(strm_port))
        with socketserver.TCPServer(("", int(strm_port)), quietHTTP) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                httpd.shutdown()
                httpd.server_close()
                sys.exit
        return None


    def run(self):
        stream_srvr = Process(target=self.serv_stream())
        stream_srvr.start()



