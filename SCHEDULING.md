# Turning a schedule request into Routines

When the owner says something like:
> "2 videos a day at 12pm and 6pm and 5 shorts a day every 2 hours starting 10AM, time zone Asia/Kolkata"

do this:

1. **Check readiness**: `bash setup.sh && python3 -m youtube.auth_check`. If credentials are missing, say what
   to fix (SETUP.md Part C) and don't create routines yet. Set `config.json` `"timezone"` to their zone.
2. **Work out the slots** (publish times). Example above:
   long: 12:00, 18:00 · short: 10:00, 12:00, 14:00, 16:00, 18:00.
3. **Fire early** so the video is ready before its slot: long ≈ **75 min early**, short ≈ **50 min early**.
   Use an odd minute (not :00/:30) to avoid scheduler load. The upload then uses `--publish-at <slot>`, so it
   goes public exactly on time.
4. **Create one Routine per slot** with `create_trigger`:
   - `create_new_session_on_fire: true` (each run starts clean in this environment)
   - `cron_expression`: `CRON_TZ=<tz> <min> <hour> * * *` (e.g. 12:00 long → `CRON_TZ=Asia/Kolkata 47 10 * * *`)
   - `name`: e.g. `Autopilot long 12:00`, `Autopilot short 14:00`
   - `prompt`: the template in ROUTINE_PROMPT.md with KIND and SLOT filled in
   - `notifications: {"push": true}` so the owner gets a phone notification per upload
   - `initiation: "human_request"`
   - If several slots share KIND and the same minute offset, one routine with a multi-hour cron is fine only if
     the prompt can derive the slot (e.g. "publish at the next full hour"). Otherwise use one routine per slot.
5. **Before enabling everything**, fire ONE routine now (`fire_trigger`) as a live test, or run the playbook
   in the current session, and confirm the upload works.
6. **Confirm back** in a small table: slot, kind, fires at, routine name. Mention the usage cost
   (each run is a full Claude session of roughly 20-45 minutes) and that the schedule can be changed any time.

## Changing or pausing
- "change shorts to 3 a day" → `list_triggers`, then `update_trigger` (cron/prompt) or create/delete as needed.
- "pause everything" → `update_trigger enabled=false` on each Autopilot routine; "resume" → `enabled=true`.
- Never create duplicate routines for the same slot; check `list_triggers` first.
