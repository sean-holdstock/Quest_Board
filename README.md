# Quest Board — Node.js

A daily fantasy quest board powered by Gemini AI. Converted from Python/Flask to Node.js/Express.

## Stack

| Layer      | Python (old)          | Node.js (new)           |
|------------|-----------------------|-------------------------|
| Server     | Flask + Gunicorn      | Express.js              |
| Templates  | Jinja2 (inline)       | express-handlebars      |
| AI         | google-genai          | @google/genai           |
| Scheduling | On-request + date check | node-cron (midnight)  |
| Process    | Gevent workers        | Node.js single process  |
| Container  | python:3.12-slim      | node:22-alpine          |

## Project Structure

```
├── src/
│   ├── app.js                  # Entry point, Express setup, cron
│   ├── routes/
│   │   └── quests.js           # GET /quest
│   ├── services/
│   │   ├── questGenerator.js   # AI generation + fallback pool
│   │   └── questCache.js       # quests.json read/write
│   └── data/
│       └── npcs.js             # NPC table, quest pools, grievances
├── views/
│   ├── layouts/main.hbs        # Base HTML layout
│   └── quest.hbs               # Quest board template
├── public/                     # Static assets (served at /static/)
│   ├── cartoon-stone-texture.png
│   └── weathered-scroll-transparent.png
├── nginx/templates/
│   └── default.conf.template   # Unchanged except port 8000 → 3000
├── Dockerfile
├── docker-compose.yml
└── package.json
```

## Setup

1. Copy your `.env` file — it needs one key:
   ```
   GEMINI_API_KEY=your-key-here
   DOMAIN_NAME=yourdomain.com
   ```

2. Copy your two PNG files into `public/`:
   - `public/cartoon-stone-texture.png`
   - `public/weathered-scroll-transparent.png`

3. Any existing `quests.json` from the Python version is **fully compatible** — same schema.

## Running locally

```bash
npm install
npm run dev        # uses --watch for auto-reload
```

Visit: http://localhost:3000/quest

## Running with Docker

```bash
docker compose up --build
```

## Routes

| Route    | Description                          |
|----------|--------------------------------------|
| `/`      | Coming soon placeholder              |
| `/quest` | The daily quest board                |

## Key differences from Python version

- **Quest regeneration** now happens via a midnight cron job (`node-cron`) rather than
  on every request with a date check. The on-request date check is still there as a safety net.
- **Static files** are now served by Express at `/static/` — the Nginx volume mount for
  static files is removed (Express handles it directly from the container).
- **No Gevent** — Node.js handles concurrency natively; no worker config needed.
