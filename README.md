# Telegram Media Extractor

A powerful Python script to safely download media (videos, photos, documents, audio) from Telegram channels, groups, or private chats.

## Features
- **Specific Media Download**: Download an exact file instantly by providing its Message ID or pasting its full Telegram link.
- **Bulk Media Scan**: Scan recent messages in a chat and download all media files found.
- **Continuous Session**: The terminal stays open in a continuous loop so you can process multiple files across different chats without restarting.
- **Any Media Type**: Automatically detects and downloads videos, photos, voice notes, and documents.
- **Smart File Naming**: Preserves original filenames when possible and uses timestamps and IDs to prevent accidental overwrites.
- **Resilient**: Safe interruption handling (downloads to `.part` until fully complete).

## Setup Instructions

### 1. Prerequisites
You need to have Python installed on your system. 
- **Windows**: Download it from the [official Python website](https://www.python.org/downloads/). During installation, make sure to check the box that says **"Add Python to PATH"**.
- **Mac**: Mac usually comes with Python, but you can install the latest version via [Homebrew](https://brew.sh/): `brew install python`.

### 2. Get your Telegram API Credentials
You need your own API ID and Hash from Telegram to use this script safely on your account.
1. Log in to your Telegram core: https://my.telegram.org/
2. Go to **API development tools**.
3. Create a new application (you can fill in anything for app title and short name).
4. Note down the **App api_id** and **App api_hash**.

### 3. Install Dependencies
Open your terminal (Mac) or Command Prompt (Windows) inside the `tg-extract` folder and run:

```bash
pip install -r requirements.txt
```
*(If `pip` doesn't work, try `pip3 install -r requirements.txt`)*

### 4. Configure Credentials
In the `tg-extract` folder, rename or copy the `.tg_env.example` file to exactly **`.tg_env`**.
Open it with any text editor and replace the placeholders with your actual credentials:

```env
TELEGRAM_API_ID=1234567
TELEGRAM_API_HASH=your_api_hash_here
```

### 5. Run the Script
Now you are ready to run the script. In your terminal/command prompt, run:

```bash
python extractor.py
```
*(If `python` doesn't work, try `python3 extractor.py`)*

### First Time Login
The very first time you run the script, it will ask for your phone number. 
**IMPORTANT:** Enter it in full international format including the `+` sign and your country code (e.g., `+15551234567` or `+447911123456`). Telegram will then send a secure login code to your app. Once logged in, a local `tg_session` file is securely created so you won't need to log in again.

### Usage
Follow the interactive on-screen menu:
1. Provide the chat name, link, or ID.
2. Select whether you want to download a specific post or scan the chat.
3. To download a specific post, simply **paste the full post link** (e.g. `https://t.me/channelname/4562`).
4. All files are safely stored inside the newly created `tg_downloads` directory!
