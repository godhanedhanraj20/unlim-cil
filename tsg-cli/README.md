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

## 📂 Where Are My Files Stored?

Your files are uploaded securely and directly to your Telegram **"Saved Messages"** chat.
This means you can easily see them on your phone, tablet, or web browser simply by opening the Telegram app and looking at your Saved Messages!

---

## ✨ Features

- **Login securely:** Uses your Telegram account (supports OTP and 2FA passwords).
- **Upload files:** Send any file up to 2GB straight to your Saved Messages.
- **List your files:** View a clean table of all the files you've stored, complete with file sizes and dates.
- **Download files:** Easily retrieve your files to your computer.
- **Delete files:** Remove files from your storage when you no longer need them.

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

## 💻 Usage (Commands)

Here is how you use the tool to manage your files.

### 📤 Upload a file
To upload a file to your storage:
```bash
python main.py upload <file_path>
```

### 📄 List your files
To see a table of the files you have stored:
```bash
python main.py list
```
If you want to see more files (up to 200), use the `--limit` option:
```bash
python main.py list --limit 100
```

### 📥 Download a file
Find the **ID** of the file you want from the `list` command, then download it:
```bash
python main.py download <id>
```

If you want to download it to a specific folder:
```bash
python main.py download <id> --output <folder_path>
```

### 🗑️ Delete a file
To remove a file from your storage forever:
```bash
python main.py delete <id>
```
*The tool will always ask you to confirm (y/n) before deleting.*

---

## 📸 Example Output

Wondering what it looks like? Here is an example of listing files:

```
Fetching files...
                             Stored Files
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃    ID ┃ Name             ┃    Size ┃ Date                ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 12345 │ vac_photo.jpg    │ 2.45 MB │ 2024-05-12 14:32:00 │
│ 12344 │ budget.pdf       │ 0.85 MB │ 2024-05-10 09:15:22 │
│ 12343 │ movie.mp4        │ 1.20 GB │ 2024-05-09 20:45:11 │
└───────┴──────────────────┴─────────┴─────────────────────┘
```

And here is what happens when you upload:

```
Uploading my_file.txt...
Upload successful
Message ID: 12346
File name: my_file.txt
File size: 12.00 KB
```

---

## ⚠️ Notes & Limitations

- **Max file size:** Telegram limits the size of a single file to **2GB**.
- **No folders:** Your files are stored in a flat list without a folder structure.
- **Storage Location:** All files are placed directly in your Telegram "Saved Messages" chat.
- **Internet:** You must be connected to the internet for the tool to work.

---

## 🛠️ Error Handling

If something goes wrong, the tool will try to give you a helpful error message. Here are some common issues:

- **"You are not logged in."** 👉 Simply run the `python main.py login` command again.
- **"File not found" or "Invalid file path."** 👉 Make sure you typed the file path or folder correctly.
- **Network issues.** 👉 Check your internet connection.
- **Config file is corrupted.** 👉 If you see this, simply delete the corrupted configuration file by deleting the `~/.tsg-cli/config.json` file on your computer, and run the login command again.

---

## 📁 Project Structure (For the curious)

If you look inside the code, here is how things are organized simply:
- **`cli/`**: Contains the code that understands the commands you type (like `upload` or `download`).
- **`services/`**: The main logic that talks to Telegram and handles logging in or moving files.
- **`telegram/`**: The connection bridge that securely connects to the Telegram network.
- **`utils/`**: Small helpers that format text (like showing "1.5 GB" instead of bytes) and handle errors.
