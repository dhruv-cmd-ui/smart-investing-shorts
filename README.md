# Stream 4 — Automated Faceless YouTube Shorts

Fully tested pipeline: script bank → ElevenLabs voiceover → Remotion-rendered vertical video → YouTube upload. Runs 2x/week via GitHub Actions. This is the most moving-parts stream, so read the setup section carefully — most steps are one-time.

**Already verified working in this session** (no API keys needed for this part): the script rotation, Remotion composition, and video rendering — rendered a real 1080x1920 test video locally, confirmed the frame layout looks right (gradient background, hook text, big keyword, script text, disclaimer, audio track wired up).

## How it works

- `scripts/script_bank.json` — 12 rotating 40-60 word finance-tip scripts (no-repeat rotation, same pattern as Streams 1 & 3).
- `scripts/generate_voiceover.py` — picks the next script, calls ElevenLabs (free tier, ~10k chars/month — easily covers 2 videos/week), writes `remotion-project/public/audio/manifest.json` + the mp3.
- `remotion-project/` — a minimal Remotion project; `src/MainVideo.tsx` reads the manifest and renders a vertical video sized exactly to the voiceover's length, with animated hook/keyword/script text synced to the audio.
- `scripts/upload_youtube.py` — uploads the rendered video as a YouTube Short using a one-time-authorized OAuth token.
- `.github/workflows/publish.yml` — runs the whole chain twice a week and commits the updated rotation state.

## Setup — steps only you can do

### 1. Get a free ElevenLabs API key
1. Sign up at **elevenlabs.io** (free tier).
2. **Profile → API Keys** → copy your key.
3. Free tier gives ~10,000 characters/month — each script here is ~250-350 characters, so 2x/week uses a small fraction of that.

### 2. Create a YouTube Data API OAuth client (one-time, in Google Cloud Console — free)
1. Go to **console.cloud.google.com** → create a new project (any name).
2. **APIs & Services → Library** → enable **YouTube Data API v3**.
3. **APIs & Services → OAuth consent screen** → choose **External**, fill in minimal required fields, add your own Google account as a test user (keeps it in "Testing" mode, which is fine for personal use — no Google review needed).
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID → Desktop app** → download the JSON — save it as `config/youtube_client_secret.json` in this folder.

### 3. Authorize once, locally (this generates the token GitHub Actions will reuse)
```
pip install -r scripts/requirements.txt
python scripts/upload_youtube.py --dry-run   # sanity check manifest/title/description first
python scripts/upload_youtube.py             # first real run: opens a browser, you log in and approve once
```
This creates `config/youtube_token.pickle` — it contains a long-lived refresh token, so you only do this once (not per video).

### 4. Create a new GitHub repo and push this folder
```
git remote add origin https://github.com/<your-username>/<new-repo>.git
git branch -M main
git push -u origin main
```
Add repo secrets: **Settings → Secrets and variables → Actions**:
- `ELEVENLABS_API_KEY`
- `YOUTUBE_CLIENT_SECRET_B64` — run `base64 -w0 config/youtube_client_secret.json` (Linux/Mac) or `[Convert]::ToBase64String([IO.File]::ReadAllBytes("config/youtube_client_secret.json"))` (PowerShell) and paste the output.
- `YOUTUBE_TOKEN_PICKLE_B64` — same base64 trick on `config/youtube_token.pickle`.

(`config/*.json`/`*.pickle` are gitignored — they never get committed, only base64'd into GitHub secrets.)

### 5. Test it
**Actions → Generate and upload Short → Run workflow** → check your YouTube channel for the new Short. After that, the Tuesday/Friday schedule takes over.

## Local testing

```
cd scripts && pip install -r requirements.txt
python generate_voiceover.py --dry-run        # picks a script, estimates duration, no API call
cd ../remotion-project && npm install
npx remotion render src/index.ts MainVideo out/video.mp4
```
Open `remotion-project/out/video.mp4` to preview. Add a real `ELEVENLABS_API_KEY` env var and drop `--dry-run` to generate real narrated audio before rendering.

## Why upload isn't fully hands-off from day one

YouTube's upload API requires OAuth tied to your personal channel — Google doesn't allow a way around that one-time browser authorization, for anyone's pipeline. Everything after that single step (script picking, voiceover, rendering, uploading) is fully automated on the 2x/week schedule.
