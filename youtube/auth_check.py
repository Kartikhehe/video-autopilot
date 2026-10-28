"""python3 -m youtube.auth_check  -> confirms the YouTube credentials work and shows which features are enabled."""
from . import api

NEED = {
    'https://www.googleapis.com/auth/youtube.upload': 'upload videos + thumbnails',
    'https://www.googleapis.com/auth/youtube.readonly': 'read stats + topic research',
    'https://www.googleapis.com/auth/youtube.force-ssl': 'post the first comment',
}


def main():
    if not api.have_creds():
        raise SystemExit('NOT SET UP: YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN are missing from the environment.')
    ch = api.my_channel()
    print('Connected to channel:', ch['snippet']['title'], f"({ch['statistics'].get('subscriberCount', '?')} subscribers)")
    scopes = set(api.token_scopes())
    for s, what in NEED.items():
        ok = s in scopes or (s.endswith('readonly') and 'https://www.googleapis.com/auth/youtube.force-ssl' in scopes)
        print(('  OK   ' if ok else '  MISSING ') + what)


if __name__ == '__main__':
    try:
        main()
    except api.YTError as e:
        raise SystemExit(f'FAILED: {e}')
