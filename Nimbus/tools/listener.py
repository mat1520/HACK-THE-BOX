import sys, re, base64, threading, json
from http.server import BaseHTTPRequestHandler, HTTPServer

LHOST, PORT = sys.argv[1], int(sys.argv[2])

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode()
        print(f"[exfil] {self.path}: {body}")
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
    do_GET = do_PUT = do_POST
    def log_message(self, *a): pass

print(f"[*] exfil listener on 0.0.0.0:{PORT}")
HTTPServer(("0.0.0.0", PORT), H).serve_forever()
