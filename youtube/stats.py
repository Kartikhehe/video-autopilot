"""python3 -m youtube.stats   -> refresh views/likes/comments for every upload and print a ranking (long and shorts)."""
import datetime
from . import api


def main():
    hist = [h for h in api.load_history() if h.get('video_id')]
    by_id = {}
    ids = [h['video_id'] for h in hist]
    for i in range(0, len(ids), 50):
        j = api.get('videos', part='statistics,status', id=','.join(ids[i:i + 50]))
        by_id.update({it['id']: it for it in j.get('items', [])})
    now = datetime.datetime.now(datetime.timezone.utc)
    for h in hist:
        it = by_id.get(h['video_id'])
        if not it:
            continue
        s = it.get('statistics', {})
        h['stats'] = dict(views=int(s.get('viewCount', 0)), likes=int(s.get('likeCount', 0)),
                          comments=int(s.get('commentCount', 0)), checked=api.now_iso())
        h['privacy'] = it.get('status', {}).get('privacyStatus', h.get('privacy'))
        if h.get('_file'):
            api.save_entry(h)
    for kind in ('long', 'short'):
        rows = [h for h in hist if h.get('kind', 'long') == kind and h.get('stats')]
        if not rows:
            continue
        print(f'\n== {kind.upper()} ==  views  likes  views/day  date        title  [topic]')
        for h in sorted(rows, key=lambda h: -h['stats']['views']):
            age = max(1, (now - datetime.datetime.fromisoformat(h['date'])).days)
            print(f"{h['stats']['views']:>14} {h['stats']['likes']:>6} {h['stats']['views'] // age:>9}  {h['date'][:10]}  "
                  f"{h['title']}  [{h.get('topic')}]")


if __name__ == '__main__':
    try:
        main()
    except api.YTError as e:
        raise SystemExit(f'FAILED: {e}')
