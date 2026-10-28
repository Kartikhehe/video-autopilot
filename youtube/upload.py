"""python3 -m youtube.upload out/<id>/metadata.json [--publish-at 18:00] [--dry-run]

Uploads the video, sets the thumbnail, posts the first comment, verifies the status and logs to history/<id>.json.
--publish-at HH:MM  (in config.json "timezone") schedules the video to go public at that time today; if that time
                    has already passed (or is < 3 min away) it is published immediately.
Exit codes: 0 ok, 2 uploaded but not public/scheduled as requested (needs attention), 1 failed.
"""
import argparse, datetime, json, os, sys
from zoneinfo import ZoneInfo
from . import api


def publish_at_iso(hhmm, tz):
    now = datetime.datetime.now(ZoneInfo(tz))
    h, m = (int(x) for x in hhmm.split(':'))
    target = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if target - now < datetime.timedelta(minutes=3):
        return None
    return target.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('metadata')
    ap.add_argument('--publish-at', help='HH:MM local time (config.json timezone)')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    with open(a.metadata) as f:
        meta = json.load(f)
    with open(os.path.join(api.ROOT, 'config.json')) as f:
        cfg = json.load(f)
    tz = cfg.get('timezone', 'UTC')
    for k in ('video', 'thumbnail'):
        if not os.path.isabs(meta[k]):
            meta[k] = os.path.join(api.ROOT, meta[k])
        if not os.path.exists(meta[k]):
            sys.exit(f'missing {k}: {meta[k]}')
    if any(h.get('id') == meta['id'] and h.get('video_id') for h in api.load_history()):
        sys.exit(f"already uploaded: {meta['id']}")
    if a.publish_at and meta.get('privacyStatus', 'public') == 'public':
        meta['publishAt'] = publish_at_iso(a.publish_at, tz)
    if a.dry_run or not api.have_creds():
        print('DRY RUN (no upload).' + ('' if api.have_creds() else ' YouTube credentials are not set.'))
        print(json.dumps({k: meta.get(k) for k in ('title', 'privacyStatus', 'publishAt', 'categoryId', 'tags', 'comment')},
                         indent=2, ensure_ascii=False))
        sys.exit(0 if a.dry_run else 1)
    ch = api.my_channel()
    print('channel:', ch['snippet']['title'])
    res = api.upload_video(meta)
    vid = res['id']
    print('uploaded:', f'https://youtu.be/{vid}', '(scheduled for ' + meta['publishAt'] + ')' if meta.get('publishAt') else '')
    thumb_ok = True
    try:
        api.set_thumbnail(vid, meta['thumbnail'])
    except api.YTError as e:
        thumb_ok = False
        print('WARNING thumbnail:', e)
    comment_ok = None
    if meta.get('comment'):
        try:
            api.post_comment(vid, meta['comment'])
            comment_ok = True
        except api.YTError as e:
            comment_ok = False
            print('WARNING comment:', e)
    st = api.video_status(vid) or res
    status = st.get('status', {})
    privacy = status.get('privacyStatus')
    entry = dict(id=meta['id'], kind=meta.get('kind', 'long'), date=api.now_iso(), topic=meta.get('topic'), title=meta['title'],
                 story=meta.get('story'), video_id=vid, url=f'https://youtu.be/{vid}', channel=ch['snippet']['title'],
                 privacy=privacy, publish_at=status.get('publishAt') or meta.get('publishAt'), thumbnail_set=thumb_ok,
                 comment_posted=comment_ok, stats={})
    api.save_entry(entry)
    wanted = meta.get('privacyStatus', 'public')
    if meta.get('publishAt'):
        if not status.get('publishAt'):
            print('ATTENTION: YouTube did not keep the scheduled publish time; the video is', privacy)
            sys.exit(2)
        print('OK scheduled', status['publishAt'])
        return
    if privacy != wanted:
        print(f'ATTENTION: requested {wanted} but YouTube set it to {privacy}. If this is "private" on every upload, '
              'the Google Cloud project needs the YouTube API audit (see SETUP.md, Troubleshooting).')
        sys.exit(2)
    print('OK', privacy)


if __name__ == '__main__':
    try:
        main()
    except api.YTError as e:
        sys.exit(f'FAILED: {e}')
