# Story Guide: how to write a video that works

Read this fully before writing a story. The quality bar is the reference video the channel owner loved
(an animated short about lust addiction: a young guy, his friends and his passion, one late-night click,
a shadow "urge" that whispers, escalation, losing friends, a failed promise and relapse, reaching out,
night-by-night recovery, back to real life). Our first video ("Lust Is Stealing Your Life") followed the
same arc with an **original** story: a guitarist, his drummer friend Dev, a missed open mic, and a
one-eyed creature that grows when fed.

## Originality rules (non-negotiable)
- Every story, scene, line and character is written fresh. **Never copy or closely paraphrase another
  creator's plot, scenes, or captions.** Research other videos only to learn *which topics people want*,
  never to borrow *what happens* in them.
- No real people, brands, logos, songs, or famous characters.
- Change the cast every video: name (if used), gender, skin tone, hair style, hoodie colour, the passion,
  the friend, the place, the goal, the habit colour and the payoff. Two videos in a row must not look alike.
  (YouTube demonetises "generic, repetitive, template-based" content. Variety is what keeps the channel
  monetisable.)

## Why the reference worked (copy the *craft*, not the content)
1. **No narrator.** Short captions over music. The viewer reads at their own pace and hears their own
   inner voice. That intimacy is the whole style.
2. **A hook line before any picture**: a universal truth on black ("Nobody plans to get stuck.").
3. **We see what he has before we see what he loses**: one passion, one friend, one goal with a deadline.
   Make them concrete and visual (a guitar, a sketchbook, a ball, a bucket drum, a poster with a date).
4. **The inciting moment is small and relatable**: boredom, loneliness, one late night, "just curious".
   The habit never looks evil at the start; it feels *good*. Show the rush honestly (sparkles, glow).
5. **The habit is personified**: a creature that **grows when fed and shrinks when starved**. It whispers
   short, persuasive lines ("just once." "you deserve it." "tomorrow."). These lines are the most quotable
   part, so write them like the real excuses people tell themselves (2-4 words).
6. **Escalation by repetition**: clocks getting later, the same shot three times with the creature bigger
   each time, diminishing returns ("the same stuff stopped hitting").
7. **The cost is shown through relationships, not lectures**: a chat thread where the friend's messages
   go from invitation → "you good?" → seen, no reply. The missed goal (empty seat, poster says TONIGHT).
8. **Honest failure**: a sincere promise ("never again") and then "2 hours later..." relapse. Viewers who
   failed before feel seen. This is what makes it emotional instead of preachy.
9. **The reframe line** at the lowest point. One sentence that changes how the viewer sees the habit
   ("It promised to make him feel good. Instead, it took everything that did." /
   "She wasn't lazy. She was scared it wouldn't be good enough.").
10. **The turn is small and real**: pick up the old passion, put the phone away, tell ONE person the truth.
11. **Recovery is a process**: a day counter (DAY 1 / 5 / 14 / 30). The creature still whispers, smaller each
    time. Day 1 is "brutal". Never pretend it's instant.
12. **The payoff calls back act 1**: the goal from the first minute happens (open mic, gallery, game, race).
    Then a closing aphorism on black ("Feed what you want to grow.") and the outro.
13. **Craft details**: captions ≤ 9 words, one idea each, 2.5-4 s on screen, third person ("he"/"she"),
    lowercase casual chat messages, warm colours for real life vs. cold/neon for the habit, slow camera
    push on every shot, silence and space before big lines.

## Story skeleton (≈150-170 s + 9 s outro)
| Act | Time | Beats | Typical templates |
|---|---|---|---|
| Hook | 0-4 s | universal truth on black | `card` |
| Who they were | 4-20 s | passion + friend + goal with deadline | `hangout` |
| The slip | 20-45 s | boredom → "just once" → the rush → creature is born (small) | `bedroom`/`desk`, `phone_feed`, `face` |
| The spiral | 45-90 s | passion feels slow, nights repeat with creature growing, diminishing returns, friend fades in chat, mirror moment, missed goal | `hangout` (distracted), `montage`, `face`, `phone_chat`, `mirror`, `hangout` (empty seat) |
| Rock bottom | 90-115 s | promise → "X hours later..." → relapse with whispers → reframe line | `bedroom` (put_away), `card`, `bedroom` (reach), `face` (sad, tear) |
| The turn | 115-130 s | picks up passion, tells the friend the truth | `bedroom` sitting_activity, `phone_chat` |
| Recovery | 130-150 s | day counter montage, creature shrinks and pops | `montage` of `bedroom`/`desk` |
| Payoff | 150-165 s | callback to the act-1 goal, crowd/cheer | `hangout` (walk_in + hi5), `stage` / `gallery` / `sunrise` |
| Close | +4 s | aphorism on black | `end_card` (outro is added automatically) |

Aim for **35-50 captions**. Total length must be **140-178 s** (the outro is included automatically).

## Topic selection
Good topics are: a habit or mindset most 15-30 year olds secretly struggle with, that **feels good short-term
and costs something precious long-term**, that can be **shown** (a device, a place, an object), and that has a
believable recovery. Examples (rotate; don't repeat a topic within 30 days):
doomscrolling / short-form video, porn & lust, gaming all night, procrastination, revenge-bedtime
procrastination (sleep), comparing yourself on social media, seeking validation/likes, junk food & sugar,
energy drinks, vaping (never show how-to), sports betting apps, overthinking, people-pleasing,
isolation & loneliness, anger, laziness vs. discipline, texting an ex / not moving on, envy of friends,
quitting too early, perfectionism, skipping the gym, wasting weekends, fake productivity.
Avoid: suicide/self-harm, eating disorders, drug instructions, politics, religion debates, medical claims.

Pick the angle that has a **surprising truth** (the reframe): procrastination → fear, scrolling → avoiding
boredom/feelings, validation → needing permission to like yourself, gaming → the only place he feels good at
something, etc. The reframe line is the heart of the video.

## Titles and thumbnails
- Title: 3-7 words, a statement with a sting, ends with a period. Pattern ideas: "X Is Stealing Your Life.",
  "What X Really Takes From You.", "He Fed It Every Night.", "The X Trap.", "Why You Can't Stop X."
  Never clickbait anything the video doesn't deliver.
- Thumbnail: a **before/after split** built from the story's own scenes (see "Thumbnails" below). The old fixed
  `variant: face` template made every video look the same, so don't use it.
- Description: 1 hook line, 2-3 sentences of what the story is about and the reframe, 2-3 practical tips,
  the closing aphorism, a soft CTA, 5-7 hashtags. Chapters are added automatically from scenes with `chapter`.

---

# Story file reference (`stories/<YYYY-MM-DD>-<slug>.json`)

```json
{
  "id": "2026-11-02-scroll",                 // unique, also the output folder name
  "topic": "doomscrolling (avoiding boredom)",
  "cast": {
    "hero":   {"skin": "#e8bf98", "hoodie": "#e3a33e", "pants": "#33405e", "hair": "#2a201c",
               "hair_style": "messy|short|bun|long|curly|cap|beanie", "shoe": "#efe9e0", "cap": "#2f6fd6", "height": 1.0},
    "friend": { ...same keys... },
    "habit":  {"glow": "#ff2e88"}               // creature + whispers colour; pick per topic
  },
  "music": {"key": 0, "tempo": 96, "seed": 1},  // key -4..+4, tempo 88-104, any seed. CHANGE EVERY VIDEO
  "scenes": [ { "template": "...", "duration": 7, "mood": "...", "chapter": "optional",
                "captions": [[start, end, "text"], ...], "params": {...}, "sfx": [[t, "boom"]],
                "fade_in": 0.35, "fade_out": 0.35 } ],
  "thumbnail": {"words": ["WHAT","LUST","TAKES."], "highlight": 1, "highlight_color": "#ff3d6e",
                "glow": "#ff8a3d", "device": "phone|laptop", "variant": "face|split",
                "split_left": {"place": "rooftop|park|street", "sky": "sunset|day|dusk|night", "activity": "guitar|sketch|camera|ball|book|idle"}},
  "youtube": {"title": "...", "description": "...", "tags": ["...", "..."],
              "comment": "first comment posted by the channel: a question that invites replies 👇"}
}
```
Times inside a scene are **seconds from the start of that scene**.

**Moods** (music + level): `warm` (strummed groove), `groove` (upbeat), `calm`, `curious` (tension starts),
`rush` (shimmer + heartbeat), `dark`, `tense` (drone + accelerating heartbeat), `numb`, `sad` (solo piano),
`tender` (picked guitar), `hope` (rising), `triumph` (full band), `silence`.

**sfx** names: `boom heartbeat whisper bucket slap click blip whoosh bell sparkle tick drawer`.
Most sounds are automatic (chat blips, taps, whispers, cheers, drawer, ticks on cards, outro clicks).

**Expressions**: `neutral happy smile bored wow dazed tired sad worried determined shock calm asleep`.
`expr` can also be keyframes: `[[0, "sad"], [3.0, "determined"]]`. Same for `clock`.

**The creature** (`urge` param, accepted by `hangout`, `bedroom`, `desk`):
`{"size": 120, "grow": 180, "x": 1150, "y": 760, "eye": 1, "mouth": 0.5, "look": [-1, 0], "alpha": 1,
  "appear_at": 2.0, "fade_in_at": 1.0, "pop_at": 2.0, "hand": [x, y],
  "whispers": [[0.8, "just once."], [3.0, "come on..."]], "say_x": 1400, "say_y": 300, "on_shoulder": true}`
Size guide: 30 = cute & harmless, 100 = present, 170 = dominant, 240 = towering. Keep whispers to 2-4 words.

## Templates
| template | what it shows | key params |
|---|---|---|
| `card` | text on black | `text`, `size` (72), `sub` |
| `hangout` | hero + friend outside | `place` rooftop/park/street, `sky` sunset/day/dusk/night/dawn, `poster` ["OPEN MIC","SAT 8PM"] (rooftop), `hero` {present, activity guitar/guitar_still/sketch/camera/ball/book/phone/idle/wave/walk_in, expr, look, x, distracted, distracted_at, bags, from_x, walk_dur}, `friend` {present, activity drum/idle/ball/wave/sit, expr, look, x}, `empty_seat`, `hi5_at`, `urge` (use `on_shoulder`), `camera` |
| `bedroom` | hero's room | `pose` lying_phone/lying_awake/asleep/reach/sitting/sitting_phone/sitting_activity/standing/empty, `activity` (for sitting_activity: guitar/sketch/camera/book), `light` night/dark/lamp/dawn/day, `clock`, `expr`, `look`, `bags`, `sweat`, `zzz`, `phone_color`, `phone_far`, `drawer_glow` (number or [t0,t1]), `reach_at`, `put_away` [t0,t1], `corner_item` guitar/ball/sketchbook/camera/shoes, `corner_glow`, `label`, `blanket`, `urge` |
| `phone_feed` | close-up, scrolling a feed, one tile glows, thumb taps | `tap_at`, `clock`, `special_color` |
| `phone_chat` | close-up chat with the friend | `contact`, `clock`, `messages` [[t,"L"/"R","text"]] (L = friend, R = hero), `typing` [t0,t1,"L"/"R"], `seen_at`, `glow` |
| `face` | big close-up for emotion | `expr`, `bg` bedroom/dark/warm, `glow` colour, `glow_amt`, `pulse`, `sparkles`, `pupil_glow`, `bags`, `tear_at`, `sweat`, `look` |
| `mirror` | bathroom mirror, creature appears behind in the reflection | `expr`, `urge_at`, `urge_size`, `bags`, `wall` |
| `desk` | hero at a desk with a laptop | `pose` typing/staring/head_down, `screen` work/feed/game/dark, `note` (sticky note text, e.g. "3 DAYS"), `papers` (pile count), `light`, `expr`, `bags`, `label`, `urge` |
| `montage` | hard cuts between shots | `shots` [{"dur": 4, "template": "bedroom", "label": "DAY 1", "params": {...}}] (durations are scaled to fit) |
| `stage` | payoff performance with crowd | `activity` guitar/speech, `friend` (bool), `cheer_at`, `banner` |
| `gallery` | payoff for creative work | `plaque`, `friend`, `cheer_at` |
| `sunrise` | quiet win, hero (+friend) watching sunrise | `activity` sit, `friend` |
| `end_card` | closing aphorism with a sprout | `text`, `sprout`, `size` |
| `outro` | added automatically (like/share/subscribe, from config.json) | none |

All templates accept `camera`: push (default), push_slow, close, pan_right, pan_left, still, or
`{"z0":1,"z1":1.1,"fx":0.5,"fy":0.5,"px0":0,"px1":-100}`.

**Extending**: if a story truly needs a new place or prop (gym, kitchen, classroom, court, bus...), add a
new template or prop to `engine/library.py` in the same flat style (thick dark outlines, flat fills, soft
glow), register it in `TEMPLATES`, document it in this table, and check it in the preview. New settings
keep the channel fresh, but never break existing templates.

---

## YouTube Shorts (`"format": "short"`)
Vertical 1080x1920, 20-59 s (aim 35-45 s). Same templates; the 16:9 scene is scaled to fill the height and a
9:16 window follows `params.focus` [x, y] (optional `focus_to` for a pan, `zoom` >= 1). Keep the hero and the
creature inside a ~600 px wide window around the focus (check the preview!).
- `"short": {"hook": {"text": "IT'S 3AM. WHY ARE YOU *STILL* *AWAKE?*", "until": 3.0, "y": 470, "size": 96},
  "highlight_color": "#ffc04d", "cover_time": 1.2, "cta": true, "cta_text": "SUBSCRIBE"}`
- Captions: <= 8 words, punchy, `*word*` highlights. They're drawn big in the lower third.
- Shot rhythm: 3-6 s per scene, ~10 scenes. Hook question in the first frame, problem → escalation →
  reframe line → small fix → payoff → one-line closer that loops back to the hook.
- No outro scene (a SUBSCRIBE pill appears automatically on the last 2.5 s). `card`/`end_card` text sizes
  must be small (~46-62) to fit the narrow frame.
- Outputs: `video.mp4`, `thumbnail.png` (1080x1920 cover with `thumbnail.badge` support), `cover_frame.png`.
  YouTube uses a frame of the Short as its cover, so the first ~1 s must look like a thumbnail.

### Thumbnails (long videos and Shorts): before/after split
The best performer ("Lust Is Stealing Your Life.") is a split: the happy life on one side, the trapped version on the
other, big faces, and 3 words ("LUST TOOK THIS."). A viewer gets it in one second. Build every thumbnail that way,
from two real scenes of the story (left/right for 16:9, top/bottom for Shorts):
```json
"thumbnail": {"layout": "scene", "slant": 70, "words": ["STUCK?"], "highlight": 0, "highlight_color": "#ffd84d",
  "title_y": 190, "title_size": 170, "shade": ["top"],
  "panels": [
    {"scene": {"template": "desk", "t": 1.0, "zoom": 1.7, "focus": [900, 640], "params": {"pose": "head_down", "expr": "sad"}},
     "label": "SITTING", "ok": false},
    {"scene": {"index": 4, "t": 3.0, "zoom": 1.55, "focus": [930, 560], "params": {"hero": {"expr": "wow"}}},
     "label": "WALKING = +60% IDEAS", "ok": true, "label_color": "#ffd84d"}]}
```
- `scene` is a scene of the story (`index`) or any template (`template` + `params`), with `params` overrides to
  sharpen the emotion. `ok` adds a green tick / red cross to the label; leave it out for BEFORE/AFTER-style labels.
- **Easy to understand first**: the title names the viewer's problem or the cost in plain words (1-4 words:
  "ANXIOUS?", "GAMING TOOK HER ART.", "1,000 VIDEOS. 0 FRIENDS."). Labels say what each side is. A number only
  goes next to what it measures ("\"THIS WEEK\" = 38%"), never alone.
- **Attention**: big faces with opposite emotions (happy/calm vs. exhausted/shocked), warm vs. cold colours, the
  creature at its biggest on the bad side.
- **Never the same twice**: vs. the last 3 uploads change the scene pair, colours, slant direction (`slant` +/-),
  title wording and layout. Don't reuse a title pattern ("X TOOK THIS.") two videos in a row.
- Faces stay visible: no text or creature on a face. Check `thumbnail_small.png`; it must read at phone size.
- Other overlays still work when they help: `big` (giant number/text, `\n` for lines), `strike`, `badge`,
  `arrows`, `rings`, `tint`. Coordinates are output pixels (1920x1080 or 1080x1920).
- Re-render only the thumbnail: `python3 -m engine.rethumb stories/<file>.json`. Replace one on YouTube:
  `python3 -m youtube.set_thumbnail <video_id> out/<id>/thumbnail.png`.

### Extra scene params (all templates)
- `thoughts`: thought bubbles `[{"t": 0.5, "until": 4, "x": 900, "y": 400, "text": "why did i SAY that??", "to": [700, 600], "size": 34}]`
- `pov: "friend"`: draw the scene from the friend's side (friend becomes the main character).
- `spotlight`: `{"x": 960, "from": 0}` darkens everything except a light cone (embarrassment, being watched).
- `hangout.extras`: background people `[{"x": 700, "expr": "neutral", "look": [0.8, 0], "look_as": {"hoodie": "#6d8f5a", "hair_style": "bun"}}]`
- Activities also include `talk` and `write` (checklist notepad). Cast option `"stain": true` puts a coffee stain on the hoodie.
- Phone chat `avatar` can be a dict of character overrides for a third person.

### Shorts that get likes
Best performers are **surprising, research-backed facts told as a tiny story**: a relatable moment → the
"wait, really?" fact (name the effect, give one concrete number) → a comforting twist → a tiny action.
Not generic advice. Cite the study in the description.
