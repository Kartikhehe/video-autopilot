"""python3 -m youtube.stats   -> refresh views/likes/comments for every uploaded video in history.json and print a ranking."""
from . import api


def main():
    hist = api.load_history()
    ids = [h['video_id'] for h in hist if h.get('video_id')]
    for i in range(0, len(ids), 50):
        j = api.get('videos', part='statistics,status', id=','.join(ids[i:i + 50]))
        by = {it['id']: it for it in j.get('items', [])}
        for h in hist:
            it = by.get(h.get('video_id'))
            if it:
                s = it.get('statistics', {})
                h['stats'] = dict(views=int(s.get('viewCount', 0)), likes=int(s.get('likeCount', 0)),
                                  comments=int(s.get('commentCount', 0)), checked=api.now_iso())
                h['privacy'] = it.get('status', {}).get('privacyStatus', h.get('privacy'))
    api.save_history(hist)
    ranked = sorted([h for h in hist if h.get('stats')], key=lambda h: -h['stats'].get('views', 0))
    print(f'{"views":>8} {"likes":>6}  date        title')
    for h in ranked:
        print(f'{h["stats"]["views"]:>8} {h["stats"]["likes"]:>6}  {h["date"][:10]}  {h["title"]}  [{h.get("topic")}]')


if __name__ == '__main__':
    try:
        main()
    except api.YTError as e:
        raise SystemExit(f'FAILED: {e}')
