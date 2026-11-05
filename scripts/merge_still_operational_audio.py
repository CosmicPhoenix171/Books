#!/usr/bin/env python3
"""Validate all Heart narration segments before publishing the audio manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BOOK=ROOT/"still-operational"
PARTS=("01","02","03","04a","04b","05","06")
source=json.loads((BOOK/"chapter-1.json").read_text(encoding="utf-8"))
paragraphs=source["paragraphs"]
expected_hash=hashlib.sha256(json.dumps(paragraphs,ensure_ascii=False,separators=(",",":")).encode("utf-8")).hexdigest()
segments=[]
all_cues=[]
last=-1
for part in PARTS:
    sidecar=json.loads((BOOK/"audio"/f"heart-{part}.json").read_text(encoding="utf-8"))
    path=BOOK/"audio"/f"heart-{part}.mp3"
    if not path.is_file() or path.stat().st_size<3000:
        raise RuntimeError(f"Missing audio for part {part}")
    if sidecar["revision_hash"]!=expected_hash or sidecar["voice"]!="af_heart":
        raise RuntimeError(f"Stale/incorrect audio part {part}")
    for cue in sidecar["cues"]:
        if cue["paragraph"]!=last+1:
            raise RuntimeError(f"Noncontiguous cue on part {part}: {cue}")
        if cue["end"]<cue["start"]:
            raise RuntimeError(f"Negative cue on part {part}")
        all_cues.append(cue)
        last=cue["paragraph"]
    segments.append({
        "file":sidecar["file"],
        "duration":sidecar["duration"],
        "firstParagraph":sidecar["cues"][0]["paragraph"],
        "lastParagraph":sidecar["cues"][-1]["paragraph"],
        "cues":sidecar["cues"],
    })
if last+1!=len(paragraphs):
    raise RuntimeError(f"Only {last+1} of {len(paragraphs)} paragraphs covered")
manifest={
    "book":"Still Operational",
    "chapter":1,
    "revision":source["revision"],
    "revision_hash":expected_hash,
    "voice":"af_heart",
    "type":"pre-rendered-mp3",
    "paragraphs":len(paragraphs),
    "totalDuration":round(sum(s["duration"] for s in segments),3),
    "segments":segments,
}
(BOOK/"audio"/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"Manifest ready: {len(segments)} MP3s, {len(all_cues)} paragraphs, {manifest['totalDuration']/60:.1f} min.")
