# Explainer channel (narrated, Kurzgesagt-inspired style)

A second, separate channel format: **5-6 minute narrated science explainers** in a flat-vector, neon-colour style
(soft glows, round characters, organs and molecules with faces, citation tags on screen). Original stories,
original art, synthesized music and sound effects, offline AI narration. Nothing is copied from other creators.

## Make an episode
```bash
bash setup.sh && pip install kokoro-onnx soundfile uharfbuzz fonttools
# voice model (once, ~350 MB):
mkdir -p /opt/tts && cd /opt/tts && \
  curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx && \
  curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd /home/user/video-autopilot
python3 -m explainer.render explainer/episodes/bhang.json --preview     # out/<id>/preview_*.jpg (2 frames/shot)
python3 -m explainer.render explainer/episodes/bhang.json --shot 8,9    # 6 frames of chosen shots
python3 -m explainer.render explainer/episodes/bhang.json --full        # video.mp4, subtitles.srt, metadata.json
python3 -m explainer.thumbs bhang|lust                                  # 3 thumbnail options per episode
python3 -m explainer.brand                                              # channel banner + avatar options
```

## Episodes
- `episodes/bhang.json`: What Bhang Really Does To Your Brain (6:00)
- `episodes/lust.json`: What Porn Actually Does To Your Brain (5:05, non-graphic by design)

## Episode file (`episodes/<slug>.json`)
- `voice` (Kokoro voice, default `af_heart`), `speed`, `music.root` (MIDI note of the key).
- `shots`: list of `{scene, say: [sentences], p: {params}, mood, cite, chapter, pad, hold}`.
  Each sentence is voiced separately; the scene receives the start time of every sentence (`beats`) so
  animations land on the words. Shots without narration use `hold` seconds.
- `mood` drives the score per bar: `bright groove hit warm wonder weird dark`.
- `cite` shows a source tag bottom-right. Every number in the script must have one. Never invent statistics.
- `tts_fix` (text substitutions) and `ipa_fix` (phoneme substitutions) fix pronunciation of Hindi words etc.
- `youtube`: title, description (sources at the end; chapters are inserted automatically), tags, first comment.

## Code
| file | what |
|---|---|
| `art.py` | drawing kit: gradients, glow, two-tone shading, people + faces, brain, glass, leaf, molecules, labels, Devanagari text |
| `scenes_a.py` | festival, shop, title, chapter cards, plant, scroll, commission, people grid, body journey, liver, graphs |
| `scenes_b.py` | neurons, lab, synapse, brain map, mice, panic/hospital, risk charts, balance, snail, keys, end card, outro |
| `scenes_c.py` | episode 2: campfire, phone feed, dopamine, wanting/liking rats, birds + giant egg, tabs, habituation, WHO file, survey grid, shame, tips, bench |
| `voice.py` | Kokoro TTS per sentence (cached in `out/_tts_cache`), timeline, SRT subtitles |
| `audio.py` | synthesized score (mood per bar), procedural SFX cued per scene, voice polish, ducking, -14 LUFS |
| `render.py` | camera push, crossfades + iris wipes, citation tags, vignette, parallel x264 encode |
| `thumbs.py` | thumbnail options |
| `brand.py`, `BRANDING.md` | channel name/banner/avatar options |
