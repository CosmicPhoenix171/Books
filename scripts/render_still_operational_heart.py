#!/usr/bin/env python3
"""Render one part of Still Operational Chapter 1 using Kokoro Heart.

Input: the published chapter-1.json, divided into contiguous, ordered sections.
Outputs: one MP3 and a timing sidecar in still-operational/audio/.
The sidecar stores measured start/end times for every spoken paragraph.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "still-operational"
PARTS = ("01", "02", "03", "04a", "04b", "05", "06")
SAMPLE_RATE = 24000
BITRATE = "80k"
VOICE = "af_heart"


def read_source(part: str):
    main = json.loads((BOOK / "chapter-1.json").read_text(encoding="utf-8"))
    full = main["paragraphs"]
    if len(full) < len(PARTS) or any(not isinstance(p, str) or not p.strip() for p in full):
        raise ValueError("Chapter 1 must contain nonempty paragraphs for every audio part.")
    part_index = PARTS.index(part)
    begin = len(full) * part_index // len(PARTS)
    end = len(full) * (part_index + 1) // len(PARTS)
    revision = hashlib.sha256(json.dumps(full, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
    return begin, full[begin:end], revision


def open_encoder(filename: Path):
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "f32le", "-ar", str(SAMPLE_RATE), "-ac", "1",
        "-i", "pipe:0", "-c:a", "libmp3lame", "-b:a", BITRATE,
        "-ar", str(SAMPLE_RATE), "-ac", "1", str(filename),
    ]
    return subprocess.Popen(command, stdin=subprocess.PIPE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", choices=PARTS, required=True)
    parser.add_argument("--model", default="models/kokoro-v1.0.int8.onnx")
    parser.add_argument("--voices", default="models/voices-v1.0.bin")
    args = parser.parse_args()
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg must be installed")
    start_offset, paragraphs, content_hash = read_source(args.part)
    folder = BOOK / "audio"
    folder.mkdir(parents=True, exist_ok=True)
    output_path = folder / f"heart-{args.part}.mp3"
    sidecar_path = folder / f"heart-{args.part}.json"

    kokoro = Kokoro(args.model, args.voices)
    encoder = open_encoder(output_path)
    t = 0.0
    cues = []
    try:
        assert encoder.stdin is not None
        for i, paragraph in enumerate(paragraphs):
            text = paragraph.strip()
            if not text:
                raise ValueError(f"Empty paragraph {i+start_offset}")
            samples, rate = kokoro.create(text, voice=VOICE, speed=1.0, lang="en-us")
            if rate != SAMPLE_RATE:
                raise RuntimeError(f"Unexpected sampling rate {rate}")
            pcm = np.asarray(samples, dtype=np.float32).reshape(-1)
            if not np.isfinite(pcm).all() or pcm.size < 300:
                raise RuntimeError(f"Bad output on paragraph {i+start_offset}")
            begin = t
            encoder.stdin.write(pcm.tobytes())
            t += pcm.size / SAMPLE_RATE
            pause = 0.16 if i + 1 < len(paragraphs) else 0.0
            if pause:
                silence = np.zeros(round(SAMPLE_RATE * pause), dtype=np.float32)
                encoder.stdin.write(silence.tobytes())
                t += len(silence) / SAMPLE_RATE
            cues.append({"paragraph": i+start_offset, "start": round(begin, 3), "end": round(t, 3)})
            if (i+1) % 20 == 0:
                print(f"{args.part}: {i+1}/{len(paragraphs)} paragraphs, {t:.1f}s audio", flush=True)
    finally:
        if encoder.stdin:
            encoder.stdin.close()
        exit_code = encoder.wait()
        if exit_code:
            raise RuntimeError(f"ffmpeg failed with code {exit_code}")

    sidecar_path.write_text(json.dumps({
        "part": args.part,
        "voice": VOICE,
        "speed": 1,
        "revision_hash": content_hash,
        "file": f"audio/heart-{args.part}.mp3",
        "duration": round(t, 3),
        "cues": cues,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    if output_path.stat().st_size < 3000:
        raise RuntimeError("MP3 is unexpectedly small")
    print(f"Completed {args.part}: {len(cues)} paragraphs, {t:.1f}s, {output_path.stat().st_size} bytes", flush=True)


if __name__ == "__main__":
    main()
