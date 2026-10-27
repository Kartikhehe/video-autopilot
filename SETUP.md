# One-time setup

✅ **Part A (GitHub) is done.** The code lives at github.com/Kartikhehe/video-autopilot.

What's left:
- **Part B**: give Claude permission to upload to your YouTube channel (about 20 minutes).
- **Part C**: save 3 secret values in Claude's settings (3 minutes).
- **Part D**: start a new session and say "set up my schedule" (1 minute).

> **Yes, you create "credentials" in the Google Cloud project.** That's step B5 below. Google calls it an
> "OAuth client" and it gives you two values: a **Client ID** and a **Client secret**. Step B6 then turns
> those into a third value, the **Refresh token**. Those 3 values are all Claude needs.

Keep a notepad open (Notes / Notepad). You'll copy 3 values into it:
```
Client ID:      ...
Client secret:  ...
Refresh token:  ...
```

---

## Part B: Google Cloud (about 20 minutes)

### B0. Use the right Google account
1. Open a **private/incognito window** in your browser.
   (Chrome: `Ctrl+Shift+N` on Windows, `Cmd+Shift+N` on Mac.)
2. Sign in to Google with **the Gmail account that owns your YouTube channel**.
   Use that same account for every step below.

### B1. Create a project (a "folder" for this app)
1. Go to **https://console.cloud.google.com**
2. If a "Welcome" popup appears: pick your country, tick the terms box, click **Agree and continue**.
3. At the very top, next to the "Google Cloud" logo, click the box that says **Select a project**
   (it may already show a project name).
4. In the window that opens, click **NEW PROJECT** (top-right of that window).
5. Project name: type `video-autopilot`. Leave everything else. Click **CREATE**.
6. Wait about 10 seconds. A notification appears; click **SELECT PROJECT**.
   ✔ The top bar now shows **video-autopilot**. Check this before every step below.

### B2. Turn on the YouTube API
1. Go to **https://console.cloud.google.com/apis/library/youtube.googleapis.com**
   (check the top bar still says **video-autopilot**).
2. Click the blue **ENABLE** button.
3. Wait until the page changes (you'll see "API enabled" or a dashboard). Done.

### B3. Fill in the app details (the "consent screen")
1. Go to **https://console.cloud.google.com/auth/overview**
2. Click **GET STARTED**.
3. **App Information**
   - App name: `video-autopilot`
   - User support email: pick your Gmail from the dropdown
   - Click **NEXT**
4. **Audience**: select **External** → **NEXT**
5. **Contact Information**: type your Gmail → **NEXT**
6. **Finish**: tick "I agree to the Google API Services: User Data Policy" → **CONTINUE** → **CREATE**

### B4. Publish the app (IMPORTANT: don't skip)
If you skip this, YouTube permission expires every 7 days and uploads stop.
1. Go to **https://console.cloud.google.com/auth/audience**
2. Under **Publishing status** it says **Testing**. Click **PUBLISH APP**.
3. A popup appears. Click **CONFIRM**.
   ✔ Publishing status now says **In production**. (You may see a note about verification. Ignore it;
   it doesn't apply because you're the only user.)

### B5. Create the credentials (OAuth client)
1. Go to **https://console.cloud.google.com/auth/clients**
2. Click **+ CREATE CLIENT** (or **+ Create credentials → OAuth client ID**).
3. **Application type**: choose **Web application**.
4. **Name**: `autopilot`
5. Scroll down to **Authorized redirect URIs** and click **+ ADD URI**.
   Paste exactly this (no spaces before or after):
   ```
   https://developers.google.com/oauthplayground
   ```
   ⚠️ Put it under **redirect URIs**, not "Authorized JavaScript origins".
6. Click **CREATE**.
7. A popup shows **Client ID** and **Client secret**.
   **Copy both into your notepad now.** Google may not show the secret again. Also click **DOWNLOAD JSON**
   as a backup.
   - Client ID looks like `123456-abc...apps.googleusercontent.com`
   - Client secret looks like `GOCSPX-...`
8. Click **OK**.

### B6. Get the Refresh token
1. Go to **https://developers.google.com/oauthplayground**
2. Click the **⚙ gear icon** in the top-right corner. A small settings panel opens:
   - Leave "OAuth flow" = **Server-side** and "Access type" = **Offline**.
   - Tick ☑ **Use your own OAuth credentials** (at the bottom).
   - Two boxes appear. Paste your **Client ID** and **Client secret** from the notepad.
   - Click the gear icon again (or anywhere outside) to close the panel.
3. Look at the **left side**, "Step 1: Select & authorize APIs". Under the long list there's a box
   that says **"Input your own scopes"**. Click it and paste exactly:
   ```
   https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly
   ```
4. Click the blue **Authorize APIs** button.
5. A Google sign-in page opens:
   - Choose **your channel's Gmail**.
   - If it asks you to **choose a channel / brand account**, pick **your YouTube channel**.
   - You'll see **"Google hasn't verified this app"**. That's normal because it's your own private app.
     Click **Advanced** (small grey link, bottom-left) → **Go to video-autopilot (unsafe)**.
   - On the permissions page, tick **all** boxes if there are checkboxes → **Continue** / **Allow**.
6. You're sent back to the playground, now on **Step 2**. Click
   **Exchange authorization code for tokens**.
7. A **Refresh token** box fills in (starts with `1//`). Copy it into your notepad.
   ✔ Your notepad now has all 3 values. Keep them private, like passwords.

### B7. Verify your channel with your phone (for custom thumbnails)
1. Go to **https://www.youtube.com/verify** (still in the channel's Gmail).
2. Enter your phone number, get the code by SMS and type it in.

---

## Part C: Save the 3 values in Claude (3 minutes)

⚠️ Never paste these into the chat. They go into the environment settings.

1. Open **https://claude.ai/code** and open a Claude Code session (this one is fine).
2. At the top of the session, click the **environment name** (in the session's title bar; it opens the
   cloud environment menu) → **Edit** next to the environment.
3. Find **Environment variables** (it may also be called **Secrets**). Add these 3 lines exactly,
   replacing the parts in `< >` with your values (no quotes, no spaces around `=`):
   ```
   YT_CLIENT_ID=<your Client ID>
   YT_CLIENT_SECRET=<your Client secret>
   YT_REFRESH_TOKEN=<your Refresh token>
   ```
4. Click **Save**.

## Part D: Turn it on (1 minute)
Settings only reach **new** sessions, so:
1. On claude.ai/code start a **New session**. Pick the **same environment** and select the
   **Kartikhehe/video-autopilot** repository.
2. Type:
   > Set up my video autopilot schedule: 1 video a day at 6pm, my time zone is Asia/Kolkata.

   (Change the number, time and time zone to what you want.)

Claude then checks the YouTube connection (it prints your channel name), makes and uploads one test
video, and creates the schedule.

### Changing the schedule later
In any session, say e.g. *"change my video routine to twice a day at 9am and 6pm"* or *"pause my video
routine"*. Or manage it at **claude.ai/code → Routines**.

### Other settings (file `config.json`)
- `"privacy"`: `"public"`, `"unlisted"` or `"private"`. Use `"private"` to review videos before publishing.
- `"channel_name"`: add your channel name once you decide; it then appears in the outro.
- `"outro_line"`: the call-to-action text at the end.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "Error 400: redirect_uri_mismatch" in B6 | In B5 the redirect URI is wrong. Open the client again and fix it to exactly `https://developers.google.com/oauthplayground`, then save and wait 1-2 minutes. |
| "Access blocked: app has not completed verification" | You skipped B4 (app still in Testing). Publish it, or add your Gmail under Audience → Test users. |
| No "Refresh token" in step B6.7 | In the gear panel, make sure Access type = **Offline** and "Use your own OAuth credentials" is ticked, then redo B6. |
| Videos upload as **Private (locked)** | Google may restrict brand-new API projects until a free audit. Search "YouTube API Services Audit and Quota Extension Form", submit it for this project ("personal tool uploading my own animated videos to my own channel"). Meanwhile set `"privacy": "private"` and publish each video in YouTube Studio with one click. |
| "invalid_grant" later | The token was revoked or the app was in Testing. Do B4, then repeat B6 and update `YT_REFRESH_TOKEN`. |
| Thumbnail not applied | Do B7 (phone verification). |
