# TSG-CLI (Telegram Storage CLI)

This tool lets you use your Telegram "Saved Messages" as a personal, free cloud storage system directly from your command line. It works like a simple personal drive, but powered by Telegram!

---

## ⚡ Quick Start

Ready to jump in? Here are the quickest steps to get started:

1. Open your terminal and run: `pip install -r requirements.txt`
2. Run the login command: `python main.py login`
3. Upload your first file: `python main.py upload my_file.txt`
4. List your files to verify: `python main.py list`

---

## ✨ Features (Full List)

- **Login securely:** Uses your Telegram account (supports OTP and optional 2FA passwords).
- **Upload files:** Send any file up to 2GB straight to your Saved Messages.
- **List your files:** View a clean table of all the files you've stored.
- **Download files:** Easily retrieve your files by their ID.
- **Delete files:** Remove files from your storage forever.
- **Search files:** Find files quickly by keyword.
- **Filter by type:** Only show videos, images, documents, or audio (`--type`).
- **Sort results:** Order your files by date, size, or name (`--sort`).
- **Limit results:** Control how many files you want to see (`--limit`).
- **Upload progress:** Watch real-time upload progress with transfer speeds (MB/s).
- **Download progress:** Watch real-time download progress with transfer speeds (MB/s).

---

## 🧠 How It Works

It is incredibly simple:
- Your files are uploaded securely and directly to your Telegram **"Saved Messages"** chat.
- Each file you upload simply becomes one Telegram message.
- The CLI uses the unique Telegram message ID as the "File ID".

This means you can easily see them on your phone, tablet, or web browser simply by opening the Telegram app and looking at your Saved Messages!

---

## 📋 Requirements

Before you begin, make sure you have:
- **Python 3.10 or newer** installed on your computer.
- A **Telegram account**.
- Your **Telegram API credentials** (we'll explain how to get these below).

---

## 🔑 How to Get Your Telegram API Credentials

To use this tool, Telegram needs to know you are authorized to connect. You'll need an `api_id` and an `api_hash`.

**Step-by-step to get them:**
1. Go to the official Telegram website: [https://my.telegram.org](https://my.telegram.org)
2. Log in using your phone number and the confirmation code sent to your Telegram app.
3. Click on **"API development tools"**.
4. Fill out the form to create a new application (you can name it anything, like "TSG-CLI").
5. Once created, you will see your **`api_id`** (a number) and your **`api_hash`** (a long string of letters and numbers). Copy these down!

---

## 🚀 Installation

Follow these steps to set up the tool on your computer:

1. **Download or clone** this project folder to your computer.
2. **Open your terminal** (or Command Prompt / PowerShell) and navigate into the `tsg-cli` folder.
3. **Install the required dependencies** by running this command:

```bash
pip install -r requirements.txt
```

---

## 🔐 First Time Setup (Login)

Before you can upload or download files, you need to log in to your Telegram account.

Run this command in your terminal:

```bash
python main.py login
```

The tool will ask you for:
1. Your **`api_id`** and **`api_hash`** (the ones you got earlier).
2. Your **phone number** (including the country code, e.g., `+1234567890`).
3. The **OTP code** that Telegram sends to your app.
4. Your **2FA password** (if you have Two-Step Verification enabled on Telegram).

🎉 **That's it!** Your login session is securely saved to your computer. You won't have to log in again unless you log out or delete the configuration file.

---

## 💻 Commands

Here is how you use the tool to manage your files.

### 🔐 login
Logs you securely into your Telegram account.
```bash
python main.py login
```

### 📤 upload
Upload a file to your storage.
```bash
python main.py upload <file>
```

### 📄 list
List the files you have stored.
```bash
python main.py list
python main.py list --sort date
python main.py list --sort size
```

### 🔍 search
Find specific files by typing a keyword.
```bash
python main.py search <query>
python main.py search <query> --type video
python main.py search <query> --sort size
python main.py search <query> --limit 20
```

### 📥 download
Download a file using its ID.
```bash
python main.py download <id>
```

### 🗑️ delete
Remove a file from your storage forever.
```bash
python main.py delete <id>
```

---

## 🌟 Real Examples

Wondering how to put it all together? Try these:

Search for a video with "pokemon" in the name, sort it by size, and only show 5 results:
```bash
python main.py search pokemon --type video --sort size --limit 5
```

List all your files alphabetically by name:
```bash
python main.py list --sort name
```

Upload a movie to your storage:
```bash
python main.py upload movie.mp4
```

---

## ⚠️ Limitations

- **Max file size:** Telegram allows a maximum of **2GB** per file.
- **No folders:** Your files are stored in a flat list without a folder structure.
- **Dependencies:** The tool depends on the Telegram API to function.
- **Internet:** You must be connected to the internet for the tool to work.

---

## 🛠️ Error Handling

If something goes wrong, the tool will try to give you a helpful error message. Here are some common issues:

- **"You are not logged in."** 👉 Simply run the `python main.py login` command again.
- **"File not found" or "Invalid file path."** 👉 Make sure you typed the file path or folder correctly.
- **Network issues.** 👉 Check your internet connection.
- **Config file is corrupted.** 👉 If you see this, simply delete the corrupted configuration file by deleting the `~/.tsg-cli/config.json` file on your computer, and run the login command again.
