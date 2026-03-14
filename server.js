// server.js — Backend proxy Node.js
// Résout le problème CORS en faisant les appels API côté serveur
// Le frontend appelle /api/... sur ce serveur, qui relaie vers Boomlify et ScraperBee

const express = require('express');
const path    = require('path');
const app     = express();
const PORT    = process.env.PORT || 3000;

app.use(express.json());

// Servir les fichiers statiques (index.html, etc.)
app.use(express.static(path.join(__dirname, 'public')));

// ════════════════════════════════════════════════
// PROXY 1 : Créer un email Boomlify
// POST /api/boomlify/create
// Body: { apiKey: "..." }
// ════════════════════════════════════════════════
app.post('/api/boomlify/create', async (req, res) => {
  const { apiKey } = req.body;
  if (!apiKey) return res.status(400).json({ error: 'apiKey manquant.' });

  try {
    const r = await fetch('https://v1.boomlify.com/api/v1/emails/create?time=1day', {
      method: 'POST',
      headers: {
        'X-API-Key':    apiKey,
        'Content-Type': 'application/json'
      }
    });
    const data = await r.json();
    if (!r.ok) return res.status(r.status).json({ error: data.message || `Boomlify ${r.status}` });
    res.json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ════════════════════════════════════════════════
// PROXY 2 : Lire les emails d'une boîte Boomlify
// POST /api/boomlify/emails
// Body: { apiKey: "...", inboxId: "..." }
// ════════════════════════════════════════════════
app.post('/api/boomlify/emails', async (req, res) => {
  const { apiKey, inboxId } = req.body;
  if (!apiKey || !inboxId) return res.status(400).json({ error: 'apiKey ou inboxId manquant.' });

  try {
    const r = await fetch('https://v1.boomlify.com/api/v1/emails?limit=10', {
      headers: {
        'X-API-Key':    apiKey,
        'X-Mailbox-Id': inboxId
      }
    });
    const data = await r.json();
    if (!r.ok) return res.status(r.status).json({ error: data.message || `Boomlify ${r.status}` });
    res.json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ════════════════════════════════════════════════
// PROXY 3 : Appel ScraperBee
// POST /api/scraperbee
// Body: { apiKey: "...", url: "...", instructions: [...], wait: 2000 }
// ════════════════════════════════════════════════
app.post('/api/scraperbee', async (req, res) => {
  const { apiKey, url, instructions, wait = 2000 } = req.body;
  if (!apiKey || !url) return res.status(400).json({ error: 'apiKey ou url manquant.' });

  try {
    const params = new URLSearchParams({
      api_key:     apiKey,
      url:         url,
      render_js:   'true',
      wait:        String(wait),
      js_scenario: JSON.stringify({ instructions })
    });

    const r = await fetch(`https://app.scrapingbee.com/api/v1/?${params.toString()}`);

    if (!r.ok) {
      const e = await r.json().catch(() => ({}));
      return res.status(r.status).json({ error: e.message || `ScraperBee ${r.status}` });
    }

    // Récupérer le résultat du evaluate() depuis le header
    const evalResult = r.headers.get('Spb-Evaluate-Result');
    res.json({ js_return_value: evalResult || null });

  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Catch-all → index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => console.log(`✅ Serveur démarré sur http://localhost:${PORT}`));

