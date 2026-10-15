from flask import Flask, jsonify, request
from flask_cors import CORS
import time, uuid, json, os

app = Flask(__name__)
CORS(app)
DB = os.path.expanduser('~/workspace/chatkoeh/db.json')

def load():
    try: return json.load(open(DB))
    except: return {'users': {}, 'messages': []}

def save(d): json.dump(d, open(DB, 'w'))

@app.route('/register', methods=['POST'])
def register():
    d = load()
    b = request.json or {}
    u, p = b.get('username','').strip(), b.get('password','')
    if not u or not p: return jsonify({'error': 'isi username & password'}), 400
    if u in d['users']: return jsonify({'error': 'username sudah dipakai'}), 400
    tok = uuid.uuid4().hex
    d['users'][u] = {'password': p, 'token': tok}
    save(d)
    return jsonify({'token': tok, 'username': u})

@app.route('/login', methods=['POST'])
def login():
    d = load()
    b = request.json or {}
    u, p = b.get('username',''), b.get('password','')
    usr = d['users'].get(u)
    if not usr or usr['password'] != p:
        return jsonify({'error': 'username/password salah'}), 401
    return jsonify({'token': usr['token'], 'username': u})

@app.route('/users')
def users():
    d = load()
    tok = request.args.get('token','')
    me = next((u for u,v in d['users'].items() if v['token']==tok), None)
    if not me: return jsonify({'error':'unauthorized'}), 401
    return jsonify({'users': [u for u in d['users'] if u != me]})

@app.route('/send', methods=['POST'])
def send():
    d = load()
    b = request.json or {}
    tok = b.get('token','')
    me = next((u for u,v in d['users'].items() if v['token']==tok), None)
    if not me: return jsonify({'error':'unauthorized'}), 401
    to, text = b.get('to',''), b.get('text','').strip()
    if not to or not text: return jsonify({'error':'tujuan & pesan wajib'}), 400
    msg = {'id': uuid.uuid4().hex[:8], 'from': me, 'to': to, 'text': text, 'ts': time.time()}
    d['messages'].append(msg)
    d['messages'] = d['messages'][-500:]
    save(d)
    return jsonify({'ok': True})

@app.route('/poll')
def poll():
    d = load()
    tok = request.args.get('token','')
    me = next((u for u,v in d['users'].items() if v['token']==tok), None)
    if not me: return jsonify({'error':'unauthorized'}), 401
    since = float(request.args.get('since','0'))
    msgs = [m for m in d['messages'] if m['ts'] > since and (m['to']==me or m['from']==me)]
    return jsonify({'messages': msgs})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8091)
