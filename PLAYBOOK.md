# Playbook: make and publish ONE video (every scheduled run)

You are the writer, director and QA for an animated self-improvement channel. Work autonomously; nobody
answers questions during a run. Produce **one** finished, original video, upload it, log it.

**Run parameters** come from the routine prompt:
- `KIND` = `long` (2:20-2:58 story, 16:9) or `short` (35-45 s, vertical 9:16)
- `SLOT` = publish time `HH:MM` in config.json `timezone` (e.g. `18:00`). The video is uploaded as scheduled and
  goes public exactly at the slot. If the run is late, it publishes immediately.
If the prompt gives no parameters, use `KIND=long` and no slot (publish immediately).

## 0. Setup (≈1 min)
```bash
cd /home/user/video-autopilot        # (clone/pull first if needed, see ROUTINE_PROMPT.md)
git pull --rebase origin main
bash setup.sh
python3 -m youtube.auth_check        # if NOT SET UP → still make the video, skip upload, report it
```

## 1. Learn from the channel
- Read `config.json`, `STORY_GUIDE.md` (all of it, every run) and the history (`history/*.json`).
- The owner sometimes uploads by hand, so also list the channel's real uploads:
  `python3 -c "from youtube import api; [print(u['published'][:10], u['title']) for u in api.channel_uploads(60)]"`.
  Treat every topic there as used. Never upload a story whose title is already on the channel (the uploader refuses it too).
- If credentials work: `python3 -m youtube.stats`. Note which topics/angles get the most **views/day** and
  **likes/view**, separately for long and short. Lean toward what works; never repeat the same topic within
  30 days (long) or the same fact/effect within 60 days (short).

## 2. Pick the topic (research ≈10 min, WebSearch with several searches sent together)
- **long**: a habit with a hidden cost + a surprising reframe (see STORY_GUIDE "Topic selection").
- **short**: a **surprising, research-backed** psychology/behaviour finding that's relatable and comforting
  or eye-opening (liking gap, spotlight effect, Zeigarnik, etc.). Not generic advice everyone knows.
  **Verify the fact with at least 2 sources**, and get one concrete number or named effect. Cite the
  study in the description. Never invent statistics.
- Optional demand check (needs credentials): `python3 -m youtube.research "<topic>" --days 180`.
- Research tells you **what people care about**, never what to copy: no plots, scenes or lines from other videos.

## 3. Write the story file
`stories/<YYYY-MM-DD>-<slug>.json` (short: add `"format": "short"`, id `<date>-short-<slug>`).
- Fresh cast/colours/music seed vs. the last 5 stories. Follow the skeleton for the KIND.
- `youtube`: `title` (short: end with ` #shorts`), `description` (hook, insight, 2-3 tips, sources for facts,
  5-7 hashtags), `tags`, and `comment`: an engaging first comment that invites replies (question + emoji).
- `thumbnail`: 2-4 words, one highlighted, plus a `badge` when a time/number makes it more clickable.
- `python3 -m engine.render stories/<file>.json --check` and fix every ERROR.

## 4. Visual QA (mandatory)
`python3 -m engine.render stories/<file>.json --preview`, then Read `out/<id>/preview.jpg` and the thumbnails
(`thumbnail.png`, `thumbnail_small.png`, plus `thumbnail_alt.png` for long or `cover_frame.png` for short).
Fix and re-preview if: a face is hidden or cut off, the creature covers a face, text overlaps text, a bubble or
whisper is cut off at the edge, a caption sits on a face, a character falls outside the vertical window (short),
or the thumbnail isn't readable small. Up to 3 rounds.
The thumbnail must be either a "hero" close-up or a before/after split that a stranger understands in one second,
and it must differ from the last 3 uploads' thumbnails (style, scene, colours, wording). See STORY_GUIDE "Thumbnails".

## 5. Render
`python3 -m engine.render stories/<file>.json --full`, then Read `out/<id>/final_sheet.jpg`. Duration must be
140-180 s (long) or 20-59 s (short).

## 6. Upload
```bash
python3 -m youtube.upload out/<id>/metadata.json --publish-at <SLOT>     # omit --publish-at if no SLOT
```
- exit 0 → done (scheduled or public). Thumbnail and comment warnings are non-fatal: mention them.
- exit 2 → uploaded but YouTube kept it private: report it clearly (API audit, see SETUP.md).
- exit 1 "credentials" → stop, report. Other failure → retry once, then report the error verbatim.
- Never upload twice in one run, and never upload a video that failed `--check`.
- YouTube has no API for pinning comments; the comment is posted, and the owner can pin it with one tap.

## 7. Save memory to git (another run may be pushing at the same time)
```bash
git add stories/ history/ engine/ STORY_GUIDE.md
git commit -m "<KIND>: <title>"
for i in 1 2 3 4; do git pull --rebase origin main && git push origin HEAD:main && break; sleep $((2**i)); done
```
`out/` is git-ignored: never commit videos.

Shorts: the Shorts feed ignores uploaded thumbnails. The designed thumbnail is baked into the first 0.3 s of the
video, so mention in the final message that the owner can set it as the cover in the YouTube app (Edit → thumbnail).

## 8. Final message (becomes the run summary / notification)
One short paragraph: KIND, title, link, scheduled time, topic + the key fact or reframe, anything needing attention.
