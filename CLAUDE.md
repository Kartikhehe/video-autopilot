# Video Autopilot

Animated self-improvement story channel. When asked to "make a video" or when a scheduled routine fires,
follow **PLAYBOOK.md** step by step. Creative rules and the story file format are in **STORY_GUIDE.md**.

- Engine: `engine/` (skia drawing, scene templates, synthesized music, thumbnails). CLI: `python3 -m engine.render`.
- YouTube: `youtube/` (upload, stats, research). Credentials come from env vars YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.
- Memory: `history.json` (every upload) + `stories/` (every story). Commit both after each run.
- Settings: `config.json` (privacy, outro text, channel name, length limits).
- Every story must be original. Never copy another creator's plot, scenes or lines.
