# Automatic Render PostgreSQL Backups to Google Drive (GitHub Actions)

## What you get
- Scheduled backups (daily at 02:00 UTC)
- Backup is created with `pg_dump` (custom format) and compressed to `.dump.gz`
- Uploaded to a Google Drive folder using a Google Service Account
- Retention: keeps the latest 30 backups (older ones are deleted)

---

## 1) Create Google Drive folder
1. Create a folder in Google Drive, e.g. `DB Backups`
2. Copy the folder ID from the URL:
   - `https://drive.google.com/drive/folders/<FOLDER_ID>`

---

## 2) Create Google Cloud Service Account (Drive API)
1. Go to Google Cloud Console
2. Create a project (or use an existing one)
3. Enable **Google Drive API**
4. Create a **Service Account**
5. Create and download a **JSON key** for the service account
6. Share your Google Drive folder with the **service account email** (Editor permission)

---

## 3) Add GitHub Secrets
In your GitHub repo:
**Settings → Secrets and variables → Actions → New repository secret**

Add these secrets:

### `DATABASE_URL`
Use the **Render PostgreSQL External Database URL**.

### `GDRIVE_FOLDER_ID`
The Google Drive folder ID from step 1.

### `GDRIVE_SA_JSON`
Paste the **entire** service account JSON (the file contents).

---

## 4) Files added in this repo
- `.github/workflows/db-backup.yml` (scheduled workflow)
- `tools/drive_backup.py` (uploads to Drive + retention)

---

## 5) Trigger a manual backup
GitHub → Actions → `Render PostgreSQL Backup` → **Run workflow**

---

## 6) Restore guide
Download a `.dump.gz` backup from Drive and run:

```bash
gunzip -c render-postgres-backup-YYYYMMDD-HHMMSS.dump.gz > backup.dump
pg_restore --clean --if-exists --no-owner --no-privileges --dbname "$DATABASE_URL" backup.dump
```

---

## Notes
- The cron schedule is in UTC.
- Retention count is currently hardcoded to 30 in the workflow step.
