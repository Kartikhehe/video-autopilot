"""python3 -m youtube.research "procrastination animated story" [--days 120] [--n 15]

Lists the most-viewed recent YouTube videos for a query (title, channel, views, views/day, length),
so a topic can be judged on real demand. Uses ~101 quota units per call (search.list has its own daily bucket).
"""
import argparse, datetime, re
from . import api


def iso_dur(s):
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', s or '')
    h, mi, se = (int(x or 0) for x in m.groups()) if m else (0, 0, 0)
    return h * 3600 + mi * 60 + se


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('query')
    ap.add_argument('--days', type=int, default=120)
    ap.add_argument('--n', type=int, default=15)
    a = ap.parse_args()
    after = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=a.days)).strftime('%Y-%m-%dT%H:%M:%SZ')
    s = api.get('search', part='snippet', q=a.query, type='video', order='viewCount', publishedAfter=after,
                maxResults=min(50, a.n), relevanceLanguage='en')
    ids = [it['id']['videoId'] for it in s.get('items', [])]
    if not ids:
        print('no results')
        return
    v = api.get('videos', part='snippet,statistics,contentDetails', id=','.join(ids))
    now = datetime.datetime.now(datetime.timezone.utc)
    rows = []
    for it in v['items']:
        pub = datetime.datetime.fromisoformat(it['snippet']['publishedAt'].replace('Z', '+00:00'))
        views = int(it['statistics'].get('viewCount', 0))
        days = max(1, (now - pub).days)
        rows.append((views, views // days, iso_dur(it['contentDetails']['duration']), it['snippet']['channelTitle'],
                     it['snippet']['title']))
    print(f'{"views":>10} {"views/day":>9} {"len":>5}  channel | title')
    for r in sorted(rows, reverse=True):
        print(f'{r[0]:>10} {r[1]:>9} {r[2] // 60:>2}:{r[2] % 60:02d}  {r[3]} | {r[4]}')


if __name__ == '__main__':
    try:
        main()
    except api.YTError as e:
        raise SystemExit(f'FAILED: {e}')
