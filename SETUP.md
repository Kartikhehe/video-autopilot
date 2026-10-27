# One-time setup (about 30-40 minutes, then it runs by itself)

You do 4 things once. After that, Claude makes and uploads videos on a schedule with no input from you.

```
Part A  GitHub         - a home for the automation's code and memory (5 min)
Part B  Google/YouTube - permission for Claude to upload to your channel (20 min)
Part C  Claude settings - paste 3 secret values into your Claude environment (3 min)
Part D  Tell Claude     - "set up the schedule" (1 min)
```

---

## Part A: GitHub (5 min)

Every run starts in a fresh, empty cloud computer. The code and the list of past videos have to live
somewhere permanent, and that's a GitHub repository.

1. Go to **github.com** and sign in (or create a free account).
2. Top-right **+** → **New repository**.
   - Name: `video-autopilot`
   - Select **Private**
   - Don't tick any boxes (no README, no .gitignore).
   - Click **Create repository**.
3. Go to **claude.ai** → click your name (bottom-left) → **Settings** → **Connectors** (or **Integrations**) →
   **GitHub** → **Connect** → approve. When GitHub asks which repositories, allow `video-autopilot`
   (or "All repositories").
4. Tell Claude: *"GitHub is connected, the repo is `<your-github-username>/video-autopilot`"*.
   Claude pushes all the code there.

---

## Part B: Google Cloud + YouTube permission (20 min)

Do this logged in with **the Gmail account that owns the YouTube channel** (your other Gmail).
Tip: use a private/incognito browser window so you don't mix up accounts.

### B1. Create a Google Cloud project
1. Open **console.cloud.google.com** → accept the terms if asked.
2. Top bar: click the project picker → **New Project** → name it `video-autopilot` → **Create**.
   Make sure it's selected in the top bar afterwards.

### B2. Turn on the YouTube API
1. Left menu (☰) → **APIs & Services** → **Library**.
2. Search **YouTube Data API v3** → click it → **Enable**.

### B3. Set up the consent screen
1. Left menu → **APIs & Services** → **OAuth consent screen** (it may be called **Google Auth Platform**).
   Click **Get started**.
2. App name: `video-autopilot`. User support email: your channel Gmail. **Next**.
3. Audience: **External**. **Next**.
4. Contact email: your channel Gmail. **Next** → tick agree → **Create**.
5. Go to **Audience** (left side) → under "Test users" click **Add users** → add your channel Gmail → **Save**.
6. Still on **Audience**: click **Publish app** → **Confirm**. Status should now say **In production**.
   ⚠️ **This step matters.** If you leave it in "Testing", the permission expires every 7 days and uploads stop.

### B4. Create the OAuth client
1. Left side → **Clients** (or **Credentials** → **+ Create credentials** → **OAuth client ID**).
2. Application type: **Web application**. Name: `autopilot`.
3. Under **Authorized redirect URIs** click **Add URI** and paste exactly:
   `https://developers.google.com/oauthplayground`
4. **Create**. A box shows **Client ID** and **Client secret**. Copy both into a note on your computer
   for the next steps.

### B5. Get the refresh token (the long-lived permission)
1. Open **developers.google.com/oauthplayground**.
2. Click the **gear icon ⚙** (top-right) → tick **Use your own OAuth credentials** → paste your
   **Client ID** and **Client secret** → close the panel.
3. On the left, find the box **"Input your own scopes"** at the bottom of Step 1 and paste:
   `https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly`
4. Click **Authorize APIs**.
   - Sign in with the **channel's Gmail**.
   - If you manage several channels, **pick the right channel** in the list.
   - You'll see "Google hasn't verified this app". That's expected because it's your own private app. Click
     **Advanced** → **Go to video-autopilot (unsafe)** → **Continue** / **Allow** (tick all boxes).
5. Back in the playground, **Step 2**: click **Exchange authorization code for tokens**.
6. Copy the **Refresh token** (starts with `1//`). Keep it secret; it's the key to your channel.

### B6. Verify the channel (needed for custom thumbnails)
Open **youtube.com/verify** with the channel account and verify with your phone number.

---

## Part C: Put the 3 secrets into Claude (3 min)

Never paste these into the chat. They go into the environment settings, which only the cloud computer can read.

1. Open this Claude Code session on **claude.ai/code**.
2. Click the **environment name** in the session's title bar → **Edit** (the cloud environment settings).
3. Under **Environment variables** (or **Network secrets** / **API credentials** if that section exists), add:
   ```
   YT_CLIENT_ID=<your Client ID>
   YT_CLIENT_SECRET=<your Client secret>
   YT_REFRESH_TOKEN=<your Refresh token>
   ```
4. **Save**. (Network access: the default/"Trusted" level already allows Google's API servers. If a run reports
   a blocked host, add `oauth2.googleapis.com` and `www.googleapis.com` under Allowed domains.)

---

## Part D: Turn on the schedule (1 min)

Start a **new** session in the same environment and say:

> *Set up my video autopilot schedule: 2 videos a day at 9am and 6pm, my time zone is <your time zone>.*

Claude then:
- checks the YouTube connection (prints your channel name),
- runs one test video end-to-end,
- creates a **Routine** (scheduled trigger) that starts a fresh session at those times. Each session
  follows `PLAYBOOK.md`: research → story → preview QA → render → thumbnail → upload → log.

### Changing the frequency later
Just tell Claude in any session, e.g. *"change my video routine to once a day at 7pm"* or
*"pause the video routine"*. You can also manage it at **claude.ai → Code → Routines**.

### Other settings (`config.json` in the repo)
- `"privacy"`: `"public"`, `"unlisted"` or `"private"`. Use `"private"` if you want to review each video first.
- `"channel_name"`: add your channel name here once you've decided; it then shows in the outro.
- `"outro_line"`: the call-to-action text.

---

## Troubleshooting

**Videos are "Private (locked)" on YouTube even though config says public.**
Google may restrict uploads from new, unaudited API projects to private. Fix: fill in Google's
*YouTube API Services - Audit and Quota Extension Form* (search that name) for your project and describe it
as "personal tool that uploads my own animated videos to my own channel". It's free and usually takes days
to a few weeks. Until then, set `"privacy": "private"` and publish each video with one click in YouTube Studio.

**"invalid_grant" / token expired.** The app is probably still in "Testing". Do B3 step 6 (Publish app), then
redo B5 and replace `YT_REFRESH_TOKEN`.

**Thumbnail not set.** Verify the channel (B6).

**Quota.** Uploads have their own daily allowance (around 100 per day by default), far more than 2 per day.
