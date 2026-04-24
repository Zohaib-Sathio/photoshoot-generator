# Photoshoot Generator — Setup

Python FastAPI backend + static HTML/CSS/JS frontend that takes mannequin
photos of a dress and generates on-model photoshoot images via OpenAI's
`gpt-image-2`.

## 1. Requirements

- Python 3.10+
- An OpenAI API key with access to `gpt-image-2`

## 2. Configure

```bash
cp .env.example .env
# then edit .env and paste your key into OPENAI_API_KEY
```

## 3. Run

**Windows:**
```
run.bat
```

**macOS / Linux:**
```bash
chmod +x run.sh
./run.sh
```

Both scripts create `.venv`, install dependencies, and start the server at
<http://localhost:8000>.

## 4. Use

1. Click **+ Add dress** (one card per outfit).
2. Drop 2–5 mannequin photos per dress (front, back, side…).
3. Set the number of shots you want per dress.
4. Tweak the prompts in the right panel if needed (Garment / Model /
   Background / Output / Poses). Each shot cycles through the pose list.
5. Click **Generate all**.
6. Download images individually or **Download all (.zip)** once the job
   finishes.

## Deploy with Docker

1. Put your keys in `.env` on the host (same format as `.env.example`).
2. Build + start:

   ```bash
   docker compose up -d --build
   ```

3. Open `http://<server>:8000`.

- Generated images persist in `./outputs/` on the host; references in `./uploads/`.
- Logs: `docker compose logs -f photoshoot`
- Update: `git pull && docker compose up -d --build`
- Stop: `docker compose down`

If you prefer plain Docker without Compose:

```bash
docker build -t photoshoot-generator .
docker run -d --name photoshoot \
  -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/outputs:/app/outputs" \
  -v "$(pwd)/uploads:/app/uploads" \
  --restart unless-stopped \
  photoshoot-generator
```

### Behind a reverse proxy

If you're fronting the container with nginx / Caddy / Traefik, point the proxy at
`http://127.0.0.1:8000` and raise the upload body limit to ~20 MB so 3-image
dress uploads aren't rejected. Example nginx:

```nginx
location / {
    client_max_body_size 20M;
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## Project layout

```
app.py                  FastAPI server + routes
image_generator.py      OpenAI gpt-image-2 wrapper (images.edit)
prompts.py              Default prompt blocks + pose library
static/                 Frontend (index.html, style.css, script.js)
uploads/                Per-job reference uploads (gitignored)
outputs/                Per-job generated PNGs (gitignored)
```

## Notes

- Generation runs sequentially on the server to stay within rate limits.
  Expect roughly 15–40 seconds per image depending on the provider.
- Image size defaults to `1024x1536` (portrait). Override with
  `OPENAI_IMAGE_SIZE` in `.env`.
- If your key uses a different image model name, set
  `OPENAI_IMAGE_MODEL=gpt-image-1` (or similar) in `.env`.
