# Automatic Render PostgreSQL Backups to Google Drive (OAuth 2.0 with personal account)

## What you get
- Scheduled backups (daily at 02:00 UTC)
- Backup is created with `pg_dump` (custom format) and compressed to `.dump.gz`
- Uploaded to a **personal Google Drive folder** using OAuth 2.0 (your account)
- Retention: keeps the latest 30 backups (older ones are deleted)

---

## 1) Create Google Drive folder
1. Create a folder in Google Drive, e.g. `DB Backups`
2. Copy the folder ID from the URL:
   - `https://drive.google.com/drive/folders/<FOLDER_ID>`

---

## 2) Create Google OAuth 2.0 Client ID (personal account)

### A) Enable Drive API
1. Go to Google Cloud Console
2. Create a project (or use existing)
3. APIs & Services → Library → Enable **Google Drive API**

### B) OAuth consent screen
1. APIs & Services → OAuth consent screen
2. Choose **External**
3. Fill:
   - App name: `Sabit Academy Backup`
   - User support email: your email
   - Developer contact: your email
4. Save and continue

### C) Create OAuth Client ID
1. APIs & Services → Credentials
2. Create Credentials → OAuth client ID
3. Application type: **Desktop app**
4. Name: `Backup Uploader`
5. Create
6. Download the JSON file

---

## 3) One-time authorization (only once)

1. Rename the downloaded JSON to `client_secret.json`
2. Place it in the repo root (or run from anywhere)
3. Run:
```bash
pip install google-auth-oauthlib
python tools/auth_drive.py
```
4. It will open a browser → log in to your Google account
5. Copy the **refresh token** printed at the end

---

## 4) Add GitHub Secrets

GitHub repo → Settings → Secrets and variables → Actions

Add these secrets:

### `DATABASE_URL`
Render PostgreSQL **External Database URL**.

### `GDRIVE_FOLDER_ID`
Your Drive folder ID from step 1.

### `GDRIVE_CLIENT_SECRET_JSON`
Paste the **full OAuth client JSON** (the file you downloaded).

### `GDRIVE_REFRESH_TOKEN`
Paste the refresh token from step 3.

---

## 5) Files added in this repo
- `.github/workflows/db-backup.yml` (scheduled workflow)
- `tools/drive_backup_oauth.py` (OAuth uploader + retention)
- `tools/auth_drive.py` (one-time auth helper)

---

## 6) Trigger a manual backup
GitHub → Actions → `Render PostgreSQL Backup` → **Run workflow**

---

## 7) Restore guide
Download a `.dump.gz` backup from Drive and run:

```bash
gunzip -c render-postgres-backup-YYYYMMDD-HHMMSS.dump.gz > backup.dump
pg_restore --clean --if-exists --no-owner --no-privileges --dbname "$DATABASE_URL" backup.dump
```

---

## Notes
- The cron schedule is in UTC.
- Retention count is currently hardcoded to 30 in the workflow step.
- Uses your personal Drive folder (no Shared Drive needed).
