"""Picks the next script (no-repeat rotation, same pattern as streams 1 & 3), generates a
voiceover via ElevenLabs free tier, and writes a manifest.json the Remotion project reads
to size the video to the actual audio length.

Free-tier friendly by design: ElevenLabs' free tier (~10k chars/month) comfortably covers
a handful of these 40-60 word scripts per week. Without an ELEVENLABS_API_KEY set, this
script still writes the manifest/script text (so the rest of the pipeline is inspectable)
but skips audio generation and tells you clearly why.
"""
import argparse
import json
import os
import random
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_BANK_PATH = Path(__file__).resolve().parent / "script_bank.json"
STATE_PATH = Path(__file__).resolve().parent / "state.json"
AUDIO_OUT_DIR = Path(__file__).resolve().parent.parent / "remotion-project" / "public" / "audio"
MANIFEST_PATH = AUDIO_OUT_DIR / "manifest.json"

VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # "George" — warm narrator, good fit for finance-tip voiceovers


def pick_script() -> dict:
    scripts = json.loads(SCRIPT_BANK_PATH.read_text(encoding="utf-8"))
    state = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.exists() else {}

    order = state.get("order")
    cursor = state.get("cursor", 0)
    if not order or len(order) != len(scripts) or cursor >= len(order):
        order = list(range(len(scripts)))
        random.shuffle(order)
        cursor = 0

    item = scripts[order[cursor]]
    state["order"] = order
    state["cursor"] = cursor + 1
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return item


def generate_audio(text: str, out_path: Path) -> float:
    """Returns duration in seconds. Raises if the ElevenLabs call fails."""
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save, VoiceSettings
    import mutagen.mp3

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=VOICE_ID,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(stability=0.8, similarity_boost=0.85, style=0.1, speed=1.0),
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    save(audio, str(out_path))
    return mutagen.mp3.MP3(str(out_path)).info.length


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Pick a script and write the manifest, but skip the ElevenLabs API call")
    args = parser.parse_args()

    item = pick_script()
    api_key = os.environ.get("ELEVENLABS_API_KEY")

    AUDIO_OUT_DIR.mkdir(parents=True, exist_ok=True)
    audio_filename = f"{item['slug']}.mp3"

    if api_key and not args.dry_run:
        duration = generate_audio(item["script"], AUDIO_OUT_DIR / audio_filename)
        print(f"Generated voiceover via ElevenLabs: {audio_filename} ({duration:.1f}s)")
    else:
        duration = round(len(item["script"].split()) / 2.5, 1)  # ~150 wpm estimate, for preview only
        print(f"No ELEVENLABS_API_KEY set (or --dry-run) — skipping real audio generation.")
        print(f"Estimated spoken duration: ~{duration}s. Set ELEVENLABS_API_KEY to generate real audio.")
        audio_filename = None

    manifest = {
        "slug": item["slug"],
        "hook": item["hook"],
        "keyword": item["keyword"],
        "script": item["script"],
        "audioFile": audio_filename,
        "durationSeconds": duration,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest written: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
