"""python3 -m youtube.set_thumbnail <video_id> <thumbnail.png>  -> replaces the thumbnail of an uploaded video."""
import sys
from . import api

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    try:
        api.set_thumbnail(sys.argv[1], sys.argv[2])
    except api.YTError as e:
        sys.exit(f'FAILED: {e}')
    print('thumbnail set:', f'https://youtu.be/{sys.argv[1]}')
