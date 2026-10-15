from http.server import BaseHTTPRequestHandler
import json, time, uuid

_store = {'users': {}, 'messages': []}

class handler(BaseHTTPRequestHandler):
    def _send(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send({})

    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/users':
            self._send({'users': list(_store['users'].keys())})
        elif path.startswith('/poll'):
            try: since = float(path.split('since=')[1].split('&')[0])
            except: since = 0
            me = path.split('user=')[1].split('&')[0] if 'user=' in path else ''
            msgs = [m for m in _store['messages'] if m['ts'] > since and (m['to']==me or m['from']==me)]
            self._send({'messages': msgs})
        else:
            self._send({'error': 'not found'}, 404)

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        try: b = json.loads(self.rfile.read(length) or b'{}')
        except: b = {}
        path = self.path.split('?')[0]

        if path == '/register':
            u, p = b.get('username','').strip(), b.get('password','')
            if not u or not p:
                return self._send({'error': 'isi username & password'}, 400)
            if u in _store['users']:
                return self._send({'error': 'username udah dipake'}, 400)
            _store['users'][u] = p
            self._send({'ok': True, 'username': u})
        elif path == '/login':
            u, p = b.get('username','').strip(), b.get('password','')
            if _store['users'].get(u) == p:
                self._send({'ok': True, 'username': u})
            else:
                self._send({'error': 'username/password salah'}, 401)
        elif path == '/send':
            frm, to, text = b.get('from',''), b.get('to',''), b.get('text','').strip()
            if not text:
                return self._send({'error': 'pesan kosong'}, 400)
            if to not in _store['users']:
                return self._send({'error': 'user tidak ada'}, 404)
            _store['messages'].append({
                'id': str(uuid.uuid4())[:8], 'from': frm, 'to': to,
                'text': text, 'ts': time.time()
            })
            self._send({'ok': True})
        else:
            self._send({'error': 'not found'}, 404)
