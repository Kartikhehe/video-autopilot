"""Minimal YouTube Data API v3 client (OAuth refresh token from environment variables).

Env vars (set once in the Claude Code cloud environment settings):
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
Scopes needed on the refresh token: youtube.upload + youtube.readonly (+ youtube.force-ssl to post comments)
"""
import json, os, sys, time, datetime
import requests

API = 'https://www.googleapis.com/youtube/v3'
UPLOAD = 'https://www.googleapis.com/upload/youtube/v3'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY = os.path.join(ROOT, 'history.json')          # legacy single file (read only)
HISTORY_DIR = os.path.join(ROOT, 'history')           # one file per upload, so parallel runs never conflict in git


class YTError(Exception):
    pass


def have_creds():
    return all(os.environ.get(k) for k in ('YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN'))


_tok = {}


def token():
    if _tok.get('exp', 0) > time.time() + 60:
        return _tok['v']
    if not have_creds():
        raise YTError('Missing YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN environment variables.')
    r = requests.post('https://oauth2.googleapis.com/token', data=dict(
        client_id=os.environ['YT_CLIENT_ID'], client_secret=os.environ['YT_CLIENT_SECRET'],
        refresh_token=os.environ['YT_REFRESH_TOKEN'], grant_type='refresh_token'), timeout=30)
    if r.status_code != 200:
        raise YTError(f'token refresh failed ({r.status_code}): {r.text[:300]}  '
                      '-> if "invalid_grant": the refresh token expired/was revoked. Make sure the OAuth app is '
                      '"In production" (not Testing) and create a new refresh token.')
    j = r.json()
    _tok.update(v=j['access_token'], exp=time.time() + j.get('expires_in', 3000))
    return _tok['v']


def _h(extra=None):
    h = {'Authorization': f'Bearer {token()}'}
    h.update(extra or {})
    return h


def get(path, **params):
    r = requests.get(f'{API}/{path}', headers=_h(), params=params, timeout=60)
    if r.status_code != 200:
        raise YTError(f'GET {path} {r.status_code}: {r.text[:400]}')
    return r.json()


def my_channel():
    j = get('channels', part='snippet,statistics', mine='true')
    if not j.get('items'):
        raise YTError('No channel found for this token. Re-authorize while picking the right channel/brand account.')
    return j['items'][0]


def upload_video(meta):
    body = dict(
        snippet=dict(title=meta['title'][:100], description=meta['description'][:5000], tags=meta.get('tags', []),
                     categoryId=meta.get('categoryId', '27'), defaultLanguage=meta.get('defaultLanguage', 'en'),
                     defaultAudioLanguage=meta.get('defaultLanguage', 'en')),
        status=dict(privacyStatus=meta.get('privacyStatus', 'public'), selfDeclaredMadeForKids=False,
                    embeddable=True, license='youtube'))
    if meta.get('publishAt'):
        body['status'].update(privacyStatus='private', publishAt=meta['publishAt'])
    size = os.path.getsize(meta['video'])
    r = requests.post(f'{UPLOAD}/videos', params=dict(uploadType='resumable', part='snippet,status'),
                      headers=_h({'Content-Type': 'application/json; charset=UTF-8', 'X-Upload-Content-Type': 'video/mp4',
                                  'X-Upload-Content-Length': str(size)}), data=json.dumps(body), timeout=60)
    if r.status_code != 200:
        raise YTError(f'upload init {r.status_code}: {r.text[:500]}')
    url = r.headers['Location']
    chunk = 16 * 1024 * 1024
    pos = 0
    with open(meta['video'], 'rb') as f:
        while True:
            f.seek(pos)
            data = f.read(chunk)
            end = pos + len(data) - 1
            for attempt in range(6):
                try:
                    rr = requests.put(url, headers=_h({'Content-Length': str(len(data)), 'Content-Range': f'bytes {pos}-{end}/{size}'}),
                                      data=data, timeout=300)
                except requests.RequestException as e:
                    rr = None
                    err = str(e)
                if rr is not None and rr.status_code in (200, 201):
                    return rr.json()
                if rr is not None and rr.status_code == 308:
                    rng = rr.headers.get('Range')
                    pos = int(rng.split('-')[1]) + 1 if rng else 0
                    break
                if rr is not None and rr.status_code not in (500, 502, 503, 504):
                    raise YTError(f'upload chunk {rr.status_code}: {rr.text[:500]}')
                time.sleep(2 ** attempt)
            else:
                raise YTError(f'upload failed after retries: {err if rr is None else rr.status_code}')


def set_thumbnail(video_id, path):
    with open(path, 'rb') as f:
        data = f.read()
    ctype = 'image/png' if path.endswith('.png') else 'image/jpeg'
    r = requests.post(f'{UPLOAD}/thumbnails/set', params=dict(videoId=video_id, uploadType='media'),
                      headers=_h({'Content-Type': ctype}), data=data, timeout=120)
    if r.status_code != 200:
        raise YTError(f'thumbnail {r.status_code}: {r.text[:300]}  (custom thumbnails need a phone-verified channel: '
                      'youtube.com/verify)')


def video_status(video_id):
    j = get('videos', part='status,snippet,statistics', id=video_id)
    return j['items'][0] if j.get('items') else None


def load_history():
    """All uploads, oldest first (merges history/*.json and the legacy history.json)."""
    out = []
    if os.path.exists(HISTORY):
        with open(HISTORY) as f:
            out.extend(json.load(f))
    if os.path.isdir(HISTORY_DIR):
        for fn in sorted(os.listdir(HISTORY_DIR)):
            if fn.endswith('.json'):
                with open(os.path.join(HISTORY_DIR, fn)) as f:
                    e = json.load(f)
                e['_file'] = fn
                out.append(e)
    return sorted(out, key=lambda e: e.get('date', ''))


def save_entry(entry):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    fn = entry.get('_file') or f"{entry['id']}.json"
    data = {k: v for k, v in entry.items() if k != '_file'}
    with open(os.path.join(HISTORY_DIR, fn), 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def post_comment(video_id, text_):
    """Top-level comment from the channel (needs youtube.force-ssl scope). YouTube has no API to pin it."""
    body = {'snippet': {'videoId': video_id, 'topLevelComment': {'snippet': {'textOriginal': text_}}}}
    r = requests.post(f'{API}/commentThreads', params={'part': 'snippet'}, headers=_h({'Content-Type': 'application/json'}),
                      data=json.dumps(body), timeout=60)
    if r.status_code != 200:
        raise YTError(f'comment {r.status_code}: {r.text[:300]}  (needs the youtube.force-ssl scope on the refresh '
                      'token, see SETUP.md B6)')
    return r.json()


def token_scopes():
    r = requests.get('https://oauth2.googleapis.com/tokeninfo', params={'access_token': token()}, timeout=30)
    return r.json().get('scope', '').split() if r.status_code == 200 else []


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
