# 🚀 TSG-CLI — Telegram Storage CLI

Use your Telegram **Saved Messages** as a personal cloud storage system.

---

## 📦 Features

### 📁 Core

* Upload files to Telegram
* Download files by ID
* Delete files
* List stored files

### 🔍 Search & Filtering

* Search by name
* Filter by file type (video, image, document, audio)
* Filter by tag
* Combine filters (name + tag + type)
* Sorting (date, size, name)
* Pagination support

### 🧠 Organization

* Tag files
* Virtual folders using tags (`--tag`)
* Rename files locally (virtual rename)

### ☁️ Backup System

* Backup metadata to Telegram
* Restore latest backup
* Restore specific backup version (`--select`)

### ⚡ UX Enhancements

* Upload/download progress bar
* Transfer speed (MB/s)
* Clean Rich table output

---

## ⚙️ Installation

```bash
git clone <your-repo-url>
cd tsg-cli
pip install -r requirements.txt
```

---

## 🔐 Login

```bash
python main.py login
```

---

## 📤 Upload

```bash
python main.py upload <file_path>
```

### Example

```bash
python main.py upload movie.mp4
```

---

## 📥 Download

```bash
python main.py download <file_id>
```

### Example

```bash
python main.py download 246810
```

---

## 📄 List Files

```bash
python main.py list
```

### Examples

```bash
# Limit results
python main.py list --limit 10

# Pagination
python main.py list --page 2

# Virtual folder (tag filter)
python main.py list --tag anime

# Combined
python main.py list --tag anime --page 2 --limit 5
```

---

## 🔍 Search

```bash
python main.py search [query]
```

### Examples

```bash
# Search by name
python main.py search pokemon

# Search by tag
python main.py search --tag anime

# Combined search
python main.py search pokemon --tag anime

# Filter by type
python main.py search .mp4 --type video

# Limit results
python main.py search pokemon --limit 20

# Pagination
python main.py search pokemon --page 2

# Full combo
python main.py search pokemon --type video --tag anime --page 1 --limit 10
```

---

## 🏷️ Tagging

```bash
python main.py tag <file_id> <action> [tag]
```

### Examples

```bash
# Add tag
python main.py tag 246810 add anime

# Remove tag
python main.py tag 246810 remove anime

# List tags
python main.py tag 246810 list
```

---

## 🗂️ Virtual Folders

Tags act as folders:

```bash
python main.py list --tag anime
```

---

## ✏️ Rename (Virtual)

```bash
python main.py rename <file_id> [new_name]
```

### Examples

```bash
# Set custom name
python main.py rename 246810 "Pokemon Episode 18"

# Remove custom name
python main.py rename 246810
```

---

## 🗑️ Delete

```bash
python main.py delete <file_id>
```

---

## ☁️ Backup

```bash
python main.py backup
```

### Example

```bash
python main.py backup
```

👉 Uploads metadata to Telegram as:

```
metadata_backup.json
```

---

## 🔄 Restore

```bash
python main.py restore
```

👉 Restores latest backup automatically

---

## 🔄 Restore (Select Version)

```bash
python main.py restore --select
```

### Example flow

```text
ID       Name                 Size     Date
246878   metadata_backup.json 228 B    2026-03-21
246876   metadata_backup.json 228 B    2026-03-21

Enter the backup ID from the table above:
```

👉 Enter ID → restore that version

---

## 🧠 How It Works

* Each file = Telegram message
* File ID = Message ID
* Files stored in **Saved Messages**
* Metadata stored locally:

```
~/.tsg-cli/metadata.json
```

* Backup stored in Telegram with tag:

```
#TSG_METADATA_BACKUP
```

---

## ⚠️ Limitations

* Depends on Telegram API
* Max file size ≈ 2GB (Telegram limit)
* Metadata is local (unless backed up)
* Backup files are hidden from normal file listings

---

## 💡 Pro Tips

* Use tags like folders (`anime`, `movies`, `docs`)
* Combine search + tag for powerful filtering
* Use rename for clean naming
* Backup before switching systems
* Use `restore --select` to rollback changes

---

## 📌 Example Workflow

```bash
# Upload file
python main.py upload movie.mp4

# Tag it
python main.py tag 246810 add movies

# Rename it
python main.py rename 246810 "Inception (2010)"

# List folder
python main.py list --tag movies

# Backup metadata
python main.py backup

# Restore later
python main.py restore --select
```

---

## 🎯 Philosophy

TSG-CLI is designed as:

```
Simple • Local-first • No database • Powered by Telegram
```

---

## 🚀 Status

✅ Phase 1 — Core CLI
✅ Phase 2 — Usability
✅ Phase 3 — Organization + Backup
