# Video Autopilot

Animated self-improvement channel: long story videos (16:9) and Shorts (9:16).

- **Make a video** (manually or when a scheduled routine fires): follow **PLAYBOOK.md** with the run parameters
  KIND (long/short) and SLOT (publish time). Creative rules + story file format: **STORY_GUIDE.md**.
- **Set up / change / pause the upload schedule** (e.g. "2 videos a day at 12pm and 6pm and 5 shorts every 2 hours
  from 10AM, Asia/Kolkata"): follow **SCHEDULING.md**, using the prompt template in **ROUTINE_PROMPT.md**.
- Engine: `engine/` (skia drawing, scene templates, shorts mode, synthesized music, thumbnails). CLI: `python3 -m engine.render`.
- YouTube: `youtube/` (auth_check, upload with --publish-at + first comment, stats, research). Credentials come from
  env vars YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.
- Memory: `history/<id>.json` (one per upload) + `stories/`. Commit both after each run (pull --rebase before push).
- Settings: `config.json` (timezone, privacy, outro text, channel name, length limits).
- Every story must be original. Never copy another creator's plot, scenes or lines. Never invent statistics.
