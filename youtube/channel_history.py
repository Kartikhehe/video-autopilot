"""python3 -m youtube.channel_history [--n 40]

The channel's memory, read straight from YouTube (works in any fresh session, no git needed):
recent uploads with kind (short/long), publish date, views, likes, views/day and title.
Use it to avoid repeating topics and to lean toward what performs.
"""
import argparse, datetime, re
from . import api


def secs(d):
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', d or '')
    h, mi, s = (int(x or 0) for x in m.groups()) if m else (0, 0, 0)
    return h * 3600 + mi * 60 + s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=40)
    a = ap.parse_args()
    up = api.get('channels', part='contentDetails', mine='true')['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    ids, tok = [], None
    while len(ids) < a.n:
        j = api.get('playlistItems', part='contentDetails', playlistId=up, maxResults=50, **({'pageToken': tok} if tok else {}))
        ids += [i['contentDetails']['videoId'] for i in j['items']]
        tok = j.get('nextPageToken')
        if not tok:
            break
    ids = ids[:a.n]
    now = datetime.datetime.now(datetime.timezone.utc)
    rows = []
    for i in range(0, len(ids), 50):
        for v in api.get('videos', part='snippet,statistics,contentDetails,status', id=','.join(ids[i:i + 50]))['items']:
            pub = datetime.datetime.fromisoformat(v['snippet']['publishedAt'].replace('Z', '+00:00'))
            st = v['statistics']
            views = int(st.get('viewCount', 0))
            rows.append((pub, 'short' if secs(v['contentDetails']['duration']) <= 180 and 'shorts' in v['snippet']['title'].lower()
                         or secs(v['contentDetails']['duration']) < 61 else 'long', views, int(st.get('likeCount', 0)),
                         views / max(1.0, (now - pub).total_seconds() / 86400), v['status']['privacyStatus'], v['snippet']['title']))
    print(f"{'date':10} {'kind':5} {'views':>6} {'likes':>5} {'v/day':>6}  title")
    for r in sorted(rows, key=lambda r: r[0], reverse=True):
        print(f"{r[0]:%Y-%m-%d} {r[1]:5} {r[2]:>6} {r[3]:>5} {r[4]:>6.0f}  {r[6]}{'' if r[5] == 'public' else '  [' + r[5] + ']'}")


if __name__ == '__main__':
    try:
        main()
    except api.YTError as e:
        raise SystemExit(f'FAILED: {e}')
