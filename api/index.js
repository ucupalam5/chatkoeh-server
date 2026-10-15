let users = {};
let messages = [];

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const url = new URL(req.url, 'http://x');
  const path = url.pathname;

  if (req.method === 'GET' && path === '/users') {
    return res.json({ users: Object.keys(users) });
  }

  if (req.method === 'GET' && path === '/poll') {
    const since = parseFloat(url.searchParams.get('since') || '0');
    const me = url.searchParams.get('user') || '';
    const msgs = messages.filter(m => m.ts > since && (m.to === me || m.from === me));
    return res.json({ messages: msgs });
  }

  if (req.method === 'POST' && path === '/register') {
    const { username, password } = req.body || {};
    const u = (username || '').trim();
    if (!u || !password) return res.status(400).json({ error: 'isi username & password' });
    if (users[u]) return res.status(400).json({ error: 'username udah dipake' });
    users[u] = password;
    return res.json({ ok: true, username: u });
  }

  if (req.method === 'POST' && path === '/login') {
    const { username, password } = req.body || {};
    const u = (username || '').trim();
    if (users[u] === password) return res.json({ ok: true, username: u });
    return res.status(401).json({ error: 'username/password salah' });
  }

  if (req.method === 'POST' && path === '/send') {
    const { from, to, text } = req.body || {};
    if (!(text || '').trim()) return res.status(400).json({ error: 'pesan kosong' });
    if (!users[to]) return res.status(404).json({ error: 'user tidak ada' });
    messages.push({ id: Math.random().toString(36).slice(2, 10), from, to, text: text.trim(), ts: Date.now() / 1000 });
    return res.json({ ok: true });
  }

  return res.status(404).json({ error: 'not found' });
}
