# from http.server import BaseHTTPRequestHandler, HTTPServer
import http.server
import json
import base64
import datetime, time, os, sys
import re

import subprocess, socketserver

import socketserver
from urllib.parse import urlparse, parse_qs
from mako.template import Template

WEB_REQURE_AUTH = True
WEB_USERNAME = "user"
WEB_PASSWORD = "pass"
SERVERPORT = 8081
HOSTNAME = ""


def render_html_homepage(query_components=None):
    if 'date_begin' in query_components:
        date_begin = query_components["date_begin"][0]
    date_today = datetime.datetime.now().strftime("%Y-%m-%d")

    htmllist = Template(filename='html/_home.html')
    html = htmllist.render(
        date_today=date_today
        )
    return html



#-----------------------------------------
# web header and handles
#-----------------------------------------
def send_img(self, filename_rel, mimetype):
    #Open the static file requested and send it
    f = open(filename_rel) 
    self.send_response(200)
    self.send_header('Content-type',mimetype)
    self.end_headers()
    self.wfile.write(f.read())
    f.close()

def content_type(filename_rel):
    ext2conttype = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif"
        }
    return ext2conttype[filename_rel[filename_rel.rfind(".")+1:].lower()]

class theWebServer(http.server.BaseHTTPRequestHandler):
    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header(
            'WWW-Authenticate', 'Basic realm="Auth Realm"')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        #------------ userauth
        if WEB_REQURE_AUTH == True:
            key = self.server.get_auth_key()

            ''' Present frontpage with user authentication. '''
            if self.headers.get('Authorization') == 'Basic ' + str(key):
                getvars = self._parse_GET()

                response = {
                    'path': self.path,
                    'get_vars': str(getvars)
                }

            else:
                self.do_AUTHHEAD()

                response = {
                    'success': False,
                    'error': 'Invalid credentials'
                }

                self.wfile.write(bytes(json.dumps(response), 'utf-8'))
                return None

        # self.send_response(301)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        length = int(self.headers['Content-Length'])
        fields = parse_qs(self.rfile.read(length).decode('utf-8'))
        html_body = None
        
        if self.path.startswith('/edit'):
            html_body = render_html_homepage(
                querycomponents=fields,
                )

        htmlwrapper = Template(filename='html/wrapper.html')
        html = htmlwrapper.render(
            body=html_body,
            )

        self.wfile.write(bytes(html, "utf-8"))

    def do_GET(self):

        #------------ userauth
        if WEB_REQURE_AUTH == True:
            key = self.server.get_auth_key()

            ''' Present frontpage with user authentication. '''
            if self.headers.get('Authorization') == 'Basic ' + str(key):
                getvars = self._parse_GET()

                response = {
                    'path': self.path,
                    'get_vars': str(getvars)
                }

            else:
                self.do_AUTHHEAD()

                response = {
                    'success': False,
                    'error': 'Invalid credentials'
                }

                self.wfile.write(bytes(json.dumps(response), 'utf-8'))
                return None


        filename =  self.path
        filename_rel = filename.strip('/')
        send_asset = False

        self.send_response(200)
        if filename[-4:] == '.html':
            self.send_header('Content-type', 'text/html')
            send_asset = True
        elif filename[-4:] == '.css':
            self.send_header('Content-type', 'text/css')
            send_asset = True
        elif filename[-5:] == '.json':
            self.send_header('Content-type', 'application/javascript')
            send_asset = True
        elif filename[-3:] == '.js':
            self.send_header('Content-type', 'application/javascript')
            send_asset = True
        elif filename[-4:] == '.ico':
            self.send_header('Content-type', 'image/x-icon')
        elif self.path.endswith(".jpg") or self.path.endswith(".gif") or self.path.endswith(".png"):
            contenttype = content_type(filename_rel)
            self.send_header('Content-type', contenttype)
            send_asset = True
        else:
            self.send_header('Content-type', 'text/html')
            send_asset = False

        self.end_headers()

        # ignore request to favicon
        if self.path.endswith('favicon.ico'):
            return
        elif send_asset or self.path.startswith('/html/assets/'):
            with open(filename_rel, 'rb') as fh:
                html = fh.read()
                self.wfile.write(html)
                return
        else:

            query_string = urlparse(self.path).query
            query_components = parse_qs(query_string)

            html_body = ""
            if self.path.startswith('/list'):
                html_body = render_html_homepage(
                    query_components=query_components
                    )
            else:
                html_body = render_html_homepage(
                    query_components=query_components
                    )

            htmlwrapper = Template(filename='html/wrapper.html')
            html = htmlwrapper.render(
                body=html_body,
                )

            self.wfile.write(bytes(html, "utf-8"))

    def _parse_GET(self):
        getvars = parse_qs(urlparse(self.path).query)

        return getvars


class CustomHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    key = ''

    def __init__(self, address, handlerClass=theWebServer):
        super().__init__(address, handlerClass)

    def set_auth(self, username, password):
        self.key = base64.b64encode(
            bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')

    def get_auth_key(self):
        return self.key


if __name__ == "__main__":        
    webServer = CustomHTTPServer(('', SERVERPORT))
    if WEB_REQURE_AUTH == True: webServer.set_auth(WEB_USERNAME, WEB_PASSWORD)
    print("Server started http://%s:%s" % (HOSTNAME, SERVERPORT))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")