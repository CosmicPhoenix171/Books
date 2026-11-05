#!/usr/bin/env python3
"""Join published Kokoro Heart MP3 parts into one downloadable chapter recording."""
from __future__ import annotations
import json
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIO=ROOT/"still-operational"/"audio"
manifest_path=AUDIO/"manifest.json"
manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
segments=manifest["segments"]
if len(segments)<2:
    raise RuntimeError("Missing narrated sections")
paths=[]
for segment in segments:
    name=Path(segment["file"]).name
    path=AUDIO/name
    if not path.is_file() or path.stat().st_size<3000:
        raise RuntimeError(f"Missing source section: {path}")
    paths.append(path.resolve())
with tempfile.TemporaryDirectory() as folder:
    listing=Path(folder)/"concat.txt"
    listing.write_text("".join("file '"+str(path).replace("'","'\\''")+"'\n" for path in paths),encoding="utf-8")
    output=AUDIO/"chapter-1-heart.mp3"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat",
                    "-safe","0","-i",str(listing),"-c","copy",str(output)],check=True)
    duration=subprocess.check_output(["ffprobe","-v","error","-show_entries",
                                       "format=duration","-of","default=noprint_wrappers=1:nokey=1",
                                       str(output)],text=True).strip()
    if abs(float(duration)-float(manifest["totalDuration"]))>2:
        raise RuntimeError("Combined chapter length does not match timing manifest")
    manifest["fullFile"]="audio/chapter-1-heart.mp3"
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Combined full chapter: {float(duration)/60:.2f} min, {output.stat().st_size} bytes")
