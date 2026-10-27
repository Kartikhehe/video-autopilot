# Video Autopilot

Claude researches a topic, writes an original animated story, renders it (video + music + thumbnail) and
uploads it to YouTube on a schedule.

- **Setup (once):** see [SETUP.md](SETUP.md)
- **What happens each run:** [PLAYBOOK.md](PLAYBOOK.md)
- **How stories are written + story file format:** [STORY_GUIDE.md](STORY_GUIDE.md)
- **Settings:** `config.json`

Manual commands:
```bash
bash setup.sh
python3 -m engine.render stories/<file>.json --check | --preview | --full
python3 -m youtube.upload out/<id>/metadata.json [--dry-run]
python3 -m youtube.stats
python3 -m youtube.research "topic animated story"
```
