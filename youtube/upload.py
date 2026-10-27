"""python3 -m youtube.upload out/<id>/metadata.json [--dry-run]

Uploads the video, sets the thumbnail, verifies the final privacy status and logs to history.json.
Exit codes: 0 ok, 2 uploaded but not public as requested (needs attention), 1 failed.
"""
import argparse, json, os, sys
from . import api


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('metadata')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    with open(a.metadata) as f:
        meta = json.load(f)
    for k in ('video', 'thumbnail'):
        if not os.path.isabs(meta[k]):
            meta[k] = os.path.join(api.ROOT, meta[k])
        if not os.path.exists(meta[k]):
            sys.exit(f'missing {k}: {meta[k]}')
    hist = api.load_history()
    if any(h.get('id') == meta['id'] and h.get('video_id') for h in hist):
        sys.exit(f"already uploaded: {meta['id']}")
    if a.dry_run or not api.have_creds():
        print('DRY RUN (no upload).' + ('' if api.have_creds() else ' YouTube credentials are not set.'))
        print(json.dumps({k: meta[k] for k in ('title', 'privacyStatus', 'categoryId', 'tags')}, indent=2))
        print(meta['description'])
        sys.exit(0 if a.dry_run else 1)
    ch = api.my_channel()
    print('channel:', ch['snippet']['title'])
    res = api.upload_video(meta)
    vid = res['id']
    print('uploaded:', f'https://youtu.be/{vid}')
    thumb_ok = True
    try:
        api.set_thumbnail(vid, meta['thumbnail'])
    except api.YTError as e:
        thumb_ok = False
        print('WARNING thumbnail:', e)
    st = api.video_status(vid) or res
    privacy = st.get('status', {}).get('privacyStatus')
    entry = dict(id=meta['id'], date=api.now_iso(), topic=meta.get('topic'), title=meta['title'], story=meta.get('story'),
                 video_id=vid, url=f'https://youtu.be/{vid}', channel=ch['snippet']['title'], privacy=privacy,
                 thumbnail_set=thumb_ok, stats={})
    hist.append(entry)
    api.save_history(hist)
    wanted = meta.get('privacyStatus', 'public')
    if not meta.get('publishAt') and privacy != wanted:
        print(f'ATTENTION: requested {wanted} but YouTube set it to {privacy}. If this is "private" on every upload, '
              'the Google Cloud project needs the YouTube API audit (see SETUP.md, "Videos stuck private").')
        sys.exit(2)
    print('OK', privacy)


if __name__ == '__main__':
    try:
        main()
    except api.YTError as e:
        sys.exit(f'FAILED: {e}')
