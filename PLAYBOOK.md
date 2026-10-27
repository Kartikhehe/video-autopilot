# Playbook: make and upload ONE video (run this every time the routine fires)

You are the writer, director and QA for an animated self-improvement channel. Work autonomously; nobody
will answer questions during a run. Produce **one** finished, original video per run, upload it, log it.

## 0. Setup (≈1 min)
```bash
cd <repo root>
bash setup.sh
```

## 1. Learn from the channel
- Read `config.json` and `history.json`.
- If YouTube credentials exist (`YT_REFRESH_TOKEN` is set), run `python3 -m youtube.stats` to refresh
  numbers. Note which topics/titles/thumbnails got the most views per day and lean toward what works
  (similar *kind* of topic or angle, never a repeat of the same topic within 30 days).

## 2. Pick today's topic (research, ≈10 min)
- Use WebSearch (several searches, sent together) for: current struggles young people talk about
  (Reddit, forums, news on habits/dopamine/screen time/sleep/loneliness), and what's performing for
  "animated story" / "self improvement animation" channels lately.
- For 2-3 candidate topics run `python3 -m youtube.research "<topic> animated story" --days 180` (needs
  credentials; skip if missing) and compare views/day. High views/day on small channels = real demand.
- Choose ONE topic using the criteria in STORY_GUIDE.md ("Topic selection"). Not used in the last 30 days
  per `history.json`. Prefer a topic with a strong, surprising reframe.
- Write a 6-line brief (in your head or as a comment in the story's `topic` field): habit, reframe line,
  hero + passion, friend, goal + payoff template, creature colour + 3 whispers.
- Research is for **demand**, not content: never reuse another video's plot, scenes or lines.

## 3. Write the story file
- Read STORY_GUIDE.md in full every run. Follow the skeleton and the craft rules.
- Create `stories/<YYYY-MM-DD>-<slug>.json` with a fresh cast (different from the last 3 videos in
  `history.json`: check their story files), new music key/tempo/seed, habit colour, title, thumbnail words,
  description, tags.
- Check: `python3 -m engine.render stories/<file>.json --check`. Fix every ERROR. Fix warnings unless
  you have a reason.

## 4. Visual QA on the preview (mandatory)
- `python3 -m engine.render stories/<file>.json --preview`
- Open `out/<id>/preview.jpg`, `out/<id>/thumbnail.png`, `out/<id>/thumbnail_small.png` and
  `out/<id>/thumbnail_alt.png` with the Read tool and **look at them**. Fix and re-preview if:
  a face is hidden or cut off, the creature covers the hero's face, whisper text overlaps something,
  captions overlap important art, a scene looks empty/broken, two scenes look identical back to back,
  or the thumbnail isn't readable at small size. Up to 3 rounds.
- If you extended `engine/library.py`, make sure the old example story still passes `--check`.

## 5. Render
- `python3 -m engine.render stories/<file>.json --full` (≈3-5 min).
- Read `out/<id>/final_sheet.jpg` as a last sanity check. Confirm with
  `ffprobe -v error -show_entries format=duration -of csv=p=0 out/<id>/video.mp4` that it's 140-180 s.

## 6. Upload
- `python3 -m youtube.upload out/<id>/metadata.json`
  - exit 0 → done.
  - exit 2 → uploaded but YouTube kept it private (API project needs the audit, see SETUP.md). Still log
    it and say so clearly in your final message.
  - exit 1 "Missing YT_..." → credentials not configured: stop here, report it (the video is not uploaded).
  - other failure → retry once; if it still fails, report the error verbatim.
- Never upload twice in one run. Never upload a video that failed `--check`.

## 7. Save memory to git
```bash
git add stories/ history.json engine/ STORY_GUIDE.md
git commit -m "Video: <title>"
git push origin HEAD
```
(Retry push up to 4 times with backoff on network errors. `out/` is git-ignored: never commit videos.)

## 8. Final message (becomes the run summary / push notification)
One short paragraph: title, YouTube link, topic + reframe line, privacy status, anything that needs the
owner's attention. No questions; this runs unattended.
