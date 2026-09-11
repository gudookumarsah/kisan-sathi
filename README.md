# Kisan Sathi — deploy guide (100% free)

## What this costs
Nothing, at pilot scale. Netlify's free tier and Gemini's free tier both cover this
comfortably. The only things you're spending are your own time and, later, an SMS/data
plan if you want to test it on your own phone.

## Step 1 — Get a free Gemini API key (2 minutes)
1. Go to https://aistudio.google.com/apikey
2. Sign in with any Google account — no credit card, no phone verification required.
3. Click "Create API key" and copy it somewhere safe.

## Step 2 — Deploy to Netlify (same way you deployed FireSafe AI)
1. Go to https://app.netlify.com and log in.
2. Drag the whole `kisan-sathi-deploy` folder onto the Netlify dashboard
   (or connect it as a Git repo if you'd rather — either works).
3. Once deployed, go to **Site settings → Environment variables** and add:
   - Key: `GEMINI_API_KEY`
   - Value: (the key you copied in Step 1)
4. Redeploy the site (Netlify does this automatically after an env var change,
   or trigger it manually from the "Deploys" tab).

That's it — the site is live at a `*.netlify.app` URL, same as your other two tools.

## Step 3 — Test it
Open the live URL, pick a crop and your market, tap "AI सल्लाह लिनुहोस्".
If it says "data.json लोड गर्न सकिएन", double check `data.json` deployed alongside
`index.html` in the same folder.

## Updating prices daily (until the scraper is built)
Open `data.json`, change the numbers under each crop's `prices`, update `date_bs`,
save, and redeploy (drag-and-drop again, or `git push` if using Git). Takes under
a minute. No code touched.

## Automating daily price updates (done — here's how to turn it on)

`scraper.py` pulls real prices from AMPIS every day and updates `data.json`
automatically, via a free GitHub Actions workflow already included in this
folder (`.github/workflows/update-prices.yml`). No servers, no cost.

**To activate it:**
1. Push this whole `kisan-sathi-deploy` folder to a GitHub repository
   (if you don't have one yet: create a free repo at github.com, then
   `git init`, `git add .`, `git commit -m "init"`, `git remote add origin <url>`,
   `git push`).
2. That's it — GitHub Actions runs automatically on the schedule set in the
   workflow file (currently ~9:15am Nepal time daily). It commits the updated
   `data.json` straight back to the repo.
3. **Connect Netlify to the same repo** (Netlify dashboard → "Add new site" →
   "Import from Git" → pick this repo) instead of drag-and-drop. Then every
   time the scraper commits an update, Netlify redeploys the site automatically
   — the whole pipeline runs itself.

See `AMPIS_PARAMETERS.md` for exactly which market/crop/date IDs the scraper
uses, and what to do when Nepal's BS calendar rolls into a new year (the one
part that needs a manual touch, once a year).

## Sharing it
No app needed — just send the live link in the ward or cooperative's existing
WhatsApp group. If adoption grows enough to justify WhatsApp Business API
later, that's a later decision, not a pilot requirement.
