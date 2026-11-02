"""python3 -m youtube.comments [--days 14]

Posts the planned first comment on recent uploads that are now PUBLIC and don't have a comment from the channel yet.
The planned text is the line starting with 💬 at the end of each video's description (added by youtube.upload),
so this works from any fresh session without git history. Needs the youtube.force-ssl scope.
YouTube has no API for pinning; pin it with one tap in the app if you like.
"""
import argparse, datetime
from . import api

MARK = '💬'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=int, default=14)
    a = ap.parse_args()
    if 'https://www.googleapis.com/auth/youtube.force-ssl' not in api.token_scopes():
        raise SystemExit('SKIP: the refresh token lacks the youtube.force-ssl scope, so comments cannot be posted. '
                         'Redo SETUP.md step B6 with all 3 scopes and update YT_REFRESH_TOKEN.')
    ch = api.my_channel()
    my_id = ch['id']
    uploads = api.get('channels', part='contentDetails', mine='true')['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    items = api.get('playlistItems', part='contentDetails', playlistId=uploads, maxResults=30)['items']
    ids = [i['contentDetails']['videoId'] for i in items]
    vids = api.get('videos', part='snippet,status', id=','.join(ids))['items'] if ids else []
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=a.days)
    posted = 0
    for v in vids:
        if v['status'].get('privacyStatus') != 'public':
            continue
        pub = datetime.datetime.fromisoformat(v['snippet']['publishedAt'].replace('Z', '+00:00'))
        if pub < cutoff:
            continue
        lines = [l for l in v['snippet'].get('description', '').splitlines() if l.strip().startswith(MARK)]
        if not lines:
            continue
        text = lines[-1].strip()[len(MARK):].strip()
        threads = api.get('commentThreads', part='snippet', videoId=v['id'], maxResults=50).get('items', [])
        mine = [t for t in threads if t['snippet']['topLevelComment']['snippet'].get('authorChannelId', {}).get('value') == my_id]
        if mine:
            continue
        try:
            api.post_comment(v['id'], text)
            posted += 1
            print('commented on', v['snippet']['title'], '->', text)
        except api.YTError as e:
            print('WARNING', v['snippet']['title'], e)
    print(f'done: {posted} comment(s) posted')


if __name__ == '__main__':
    try:
        main()
    except api.YTError as e:
        raise SystemExit(f'FAILED: {e}')
