// server.js — Backend proxy Node.js

const express = require('express');
const path    = require('path');
const app     = express();
const PORT    = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ════════════════════════════════════════════════
// PROXY 1 : Créer un email pindush.net via ScraperBee
// sur boomlify.com (navigation réelle, sans API Boomlify)
// POST /api/boomlify/create
// Body: { scraperBeeKey: "..." }
// ════════════════════════════════════════════════
app.post('/api/boomlify/create', async (req, res) => {
  const { scraperBeeKey } = req.body;
  if (!scraperBeeKey) return res.status(400).json({ error: 'scraperBeeKey manquant.' });

  try {
    // ScraperBee navigue sur boomlify.com et :
    // 1. Attend que la page charge et affiche un email
    // 2. Cherche le bouton/select pour changer de domaine vers pindush.net
    // 3. Sélectionne dev.pindush.net et récupère l'adresse générée
    const params = new URLSearchParams({
      api_key:     scraperBeeKey,
      url:         'https://boomlify.com/',
      render_js:   'true',
      wait:        '4000',
      js_scenario: JSON.stringify({
        instructions: [
          // Attendre que la page soit complètement chargée
          { wait: 3000 },

          // Script : sélectionner pindush.net dans le dropdown de domaine
          // et récupérer l'email généré
          {
            evaluate: `
              (() => {
                // Chercher tous les éléments qui ressemblent à un sélecteur de domaine
                // Boomlify affiche un dropdown avec les domaines disponibles
                function trySelectDomain() {
                  // Essayer les select natifs
                  const selects = [...document.querySelectorAll('select')];
                  for (const sel of selects) {
                    const opts = [...sel.options];
                    const dev.pindushOpt = opts.find(o =>
                      o.value.includes('dev.pindush') || o.text.includes('dev.pindush')
                    );
                    if (pindushOpt) {
                      sel.value = dev.pindushOpt.value;
                      sel.dispatchEvent(new Event('change', { bubbles: true }));
                      return 'select_found';
                    }
                  }

                  // Essayer les boutons/liens contenant "dev.pindush"
                  const allEls = [...document.querySelectorAll('button, a, li, span, div')];
                  const dev.pindushEl = allEls.find(el =>
                    el.textContent.includes('@dev.pindush.net') ||
                    el.getAttribute('data-domain')?.includes('dev.pindush')
                  );
                  if (dev.pindushEl) {
                    dev.pindushEl.click();
                    return 'element_clicked';
                  }

                  return 'not_found';
                }

                return trySelectDomain();
              })()
            `
          },

          // Attendre que le domaine soit appliqué et l'email régénéré
          { wait: 2500 },

          // Récupérer l'adresse email affichée
          {
            evaluate: `
              (() => {
                // Stratégie 1 : chercher un input avec l'email
                const inputs = [...document.querySelectorAll('input[type="text"], input[type="email"], input[readonly]')];
                for (const inp of inputs) {
                  const val = inp.value.trim();
                  if (val.includes('@') && val.includes('.')) return val;
                }

                // Stratégie 2 : chercher dans les éléments texte
                const textEls = [...document.querySelectorAll('span, p, div, h1, h2, h3, td, code')];
                for (const el of textEls) {
                  const txt = el.textContent.trim();
                  // Regex email basique
                  const match = txt.match(/[a-zA-Z0-9._%+\\-]+@[a-zA-Z0-9.\\-]+\\.[a-zA-Z]{2,}/);
                  if (match) return match[0];
                }

                // Stratégie 3 : chercher dans le DOM complet
                const bodyText = document.body.innerText;
                const emailMatch = bodyText.match(/[a-zA-Z0-9._%+\\-]+@pindush\\.net/);
                if (emailMatch) return emailMatch[0];

                // Fallback : n'importe quel email trouvé
                const anyEmail = bodyText.match(/[a-zA-Z0-9._%+\\-]+@[a-zA-Z0-9.\\-]+\\.[a-zA-Z]{2,}/);
                return anyEmail ? anyEmail[0] : 'EMAIL_NON_TROUVE';
              })()
            `
          }
        ]
      })
    });

    const r = await fetch(`https://app.scrapingbee.com/api/v1/?${params.toString()}`);

    if (!r.ok) {
      const e = await r.json().catch(() => ({}));
      return res.status(r.status).json({ error: e.message || `ScraperBee ${r.status}` });
    }

    // L'email est dans le header Spb-Evaluate-Result du dernier evaluate()
    const email = r.headers.get('Spb-Evaluate-Result')?.replace(/^"|"$/g, '').trim();

    if (!email || email === 'EMAIL_NON_TROUVE' || !email.includes('@')) {
      console.error('Email non trouvé — réponse ScraperBee headers:', [...r.headers.entries()]);
      return res.status(500).json({ error: 'Email non trouvé sur boomlify.com. Vérifie que pindush.net est disponible.' });
    }

    console.log(`Email Boomlify créé : ${email}`);
    res.json({ email, address: email, id: email.split('@')[0] });

  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ════════════════════════════════════════════════
// PROXY 2 : Lire les emails d'une boîte Boomlify
// ScraperBee navigue sur boomlify.com et lit les messages
// POST /api/boomlify/emails
// Body: { scraperBeeKey: "...", email: "..." }
// ════════════════════════════════════════════════
app.post('/api/boomlify/emails', async (req, res) => {
  const { scraperBeeKey, email } = req.body;
  if (!scraperBeeKey || !email) return res.status(400).json({ error: 'scraperBeeKey ou email manquant.' });

  try {
    const params = new URLSearchParams({
      api_key:     scraperBeeKey,
      url:         'https://boomlify.com/',
      render_js:   'true',
      wait:        '4000',
      js_scenario: JSON.stringify({
        instructions: [
          { wait: 3000 },

          // Saisir l'email dans la boîte de recherche si nécessaire
          {
            evaluate: `
              (() => {
                // Sur boomlify.com, essayer de naviguer vers la boîte de l'email
                const inputs = [...document.querySelectorAll('input[type="text"], input[type="email"]')];
                const emailInput = inputs.find(i =>
                  i.placeholder?.toLowerCase().includes('email') ||
                  i.name?.toLowerCase().includes('email')
                );
                if (emailInput) {
                  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                  setter.call(emailInput, '${email}');
                  emailInput.dispatchEvent(new Event('input', { bubbles: true }));
                  emailInput.dispatchEvent(new Event('change', { bubbles: true }));
                  return 'input_filled';
                }
                return 'no_input';
              })()
            `
          },
          { wait: 2000 },

          // Récupérer les emails reçus
          {
            evaluate: `
              (() => {
                const emails = [];

                // Chercher les éléments qui ressemblent à des emails reçus
                const rows = [...document.querySelectorAll('[class*="inbox"], [class*="email"], [class*="mail"], [class*="message"], tr, li')];
                for (const row of rows) {
                  const txt = row.textContent.trim();
                  // Un email de confirmation contient souvent "confirm", "verify", "activate"
                  if (txt.length > 10 && txt.length < 2000) {
                    // Chercher un lien de confirmation dans cet élément
                    const links = [...row.querySelectorAll('a')];
                    const confirmLink = links.find(a =>
                      /confirm|verify|activate|token|validate/i.test(a.href + a.textContent)
                    );
                    if (confirmLink) {
                      emails.push({
                        subject: txt.slice(0, 100),
                        body_html: row.innerHTML,
                        confirmLink: confirmLink.href
                      });
                    }
                  }
                }

                // Fallback : chercher tous les liens de confirmation dans la page
                if (emails.length === 0) {
                  const allLinks = [...document.querySelectorAll('a')];
                  const confirmLinks = allLinks.filter(a =>
                    /confirm|verify|activate|token|validate/i.test(a.href)
                  );
                  confirmLinks.forEach(a => emails.push({
                    subject: 'Confirmation email',
                    body_html: '<a href="' + a.href + '">' + a.href + '</a>',
                    confirmLink: a.href
                  }));
                }

                return JSON.stringify(emails);
              })()
            `
          }
        ]
      })
    });

    const r = await fetch(`https://app.scrapingbee.com/api/v1/?${params.toString()}`);

    if (!r.ok) {
      const e = await r.json().catch(() => ({}));
      return res.status(r.status).json({ error: e.message || `ScraperBee ${r.status}` });
    }

    const raw = r.headers.get('Spb-Evaluate-Result') || '[]';
    let emails = [];
    try {
      const parsed = JSON.parse(raw.replace(/^"|"$/g, ''));
      emails = typeof parsed === 'string' ? JSON.parse(parsed) : parsed;
    } catch { emails = []; }

    console.log(`Boomlify inbox — ${emails.length} email(s) trouvé(s)`);
    res.json({ emails, data: emails });

  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// ════════════════════════════════════════════════
// PROXY 3 : Appel ScraperBee générique
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

