import os
import asyncio
from pathlib import Path
from telethon import TelegramClient
from dotenv import load_dotenv

# Everything (credentials, session file, downloads) lives next to this script
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".tg_env"

if not ENV_PATH.exists():
    print(f"Error: credentials file not found at {ENV_PATH}")
    print("Create it by renaming/copying '.tg_env.example' to '.tg_env' and adding your credentials.")
    exit(1)

load_dotenv(ENV_PATH)
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

if not api_id or not api_hash:
    print(f"Error: TELEGRAM_API_ID or TELEGRAM_API_HASH missing in {ENV_PATH}")
    exit(1)

if not api_id.strip().isdigit():
    print("Error: TELEGRAM_API_ID must be a number. It still looks like a placeholder.")
    exit(1)

DOWNLOAD_DIR = BASE_DIR / "tg_downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

client = TelegramClient(str(BASE_DIR / "tg_session"), int(api_id), api_hash.strip())

async def find_chat(query):
    print(f"Looking for {query}...")
    # 1) Try as numeric ID, link or username
    try:
        target = int(query) if query.lstrip("-").isdigit() else query
        return await client.get_entity(target)
    except Exception:
        pass

    # 2) Search your own chats by title (works for group/channel names you are a member of)
    print("Not a direct link/ID, searching your chats by name...")
    matches = []
    async for dialog in client.iter_dialogs():
        if query.lower() in (dialog.name or "").lower():
            matches.append(dialog)

    if not matches:
        print("No chat found with that name. Here are all your chats:\n")
        async for dialog in client.iter_dialogs():
            print(f"  {dialog.id}  |  {dialog.name}")
        print("\nRun again and enter the number from the left column (or part of the name).")
        return None

    if len(matches) == 1:
        print(f"Found: {matches[0].name} (ID {matches[0].id})")
        return matches[0].entity

    print("Multiple matches:")
    for i, d in enumerate(matches, 1):
        print(f"  {i}. {d.name}  (ID {d.id})")
    try:
        choice = int(input("Pick a number: "))
        return matches[choice - 1].entity
    except Exception:
        print("Invalid choice.")
        return None

async def download_message_media(message):
    """Downloads media from a single message if it exists."""
    if not message.media:
        return False

    date_str = message.date.strftime("%Y-%m-%d")
    
    # Try to get the original filename, otherwise create one based on extension
    filename = message.file.name if hasattr(message.file, 'name') and message.file.name else None
    if not filename:
        ext = message.file.ext if hasattr(message.file, 'ext') and message.file.ext else ".bin"
        filename = f"media_{message.id}{ext}"
    
    # Prepend date and message ID to ensure uniqueness
    final_name = f"{date_str}_{message.id}_{filename}"
    filepath = DOWNLOAD_DIR / final_name

    if filepath.exists():
        print(f"Skipping (already downloaded): {final_name}")
        return True

    print(f"Found media (Message ID: {message.id}). Downloading to {final_name}...")
    part = filepath.with_suffix(filepath.suffix + ".part")
    await client.download_media(message, file=str(part))
    part.rename(filepath)
    print(f"✅ Downloaded {final_name}")
    return True

async def main():
    print("\nConnecting to Telegram...")
    await client.start()

    current_channel = None

    while True:
        print("\n" + "="*50)
        print("--- Telegram Media Extractor ---")
        
        if current_channel:
            # Try to get a human-readable name for the current chat
            chat_name = getattr(current_channel, 'title', getattr(current_channel, 'username', 'Unknown Chat'))
            print(f"Current Chat: {chat_name}")
            print("1. Download specific media from this chat (Default)")
            print("2. Scan this chat for multiple recent media")
            print("3. Switch to a DIFFERENT chat")
            print("4. Exit")
            
            choice = input("\nSelect an option (1-4) [Default: 1]: ").strip()
            if not choice:
                choice = "1"
                
            if choice == "4":
                print("Exiting... Have a great day!")
                break
            elif choice == "3":
                current_channel = None
                continue
            elif choice not in ["1", "2"]:
                print("Invalid choice. Try again.")
                continue
        else:
            print("1. Download a specific file/media")
            print("2. Scan a chat for multiple recent media")
            print("3. Exit")
            
            choice = input("\nSelect an option (1-3): ").strip()
            if choice == "3":
                print("Exiting... Have a great day!")
                break
            elif choice not in ["1", "2"]:
                print("Invalid choice. Try again.")
                continue
                
            channel_link = input("\nEnter the chat name, link, or ID: ").strip()
            channel = await find_chat(channel_link)
            if not channel:
                continue
            current_channel = channel

        if choice == "1":
            msg_id_input = input("\nEnter the specific Message ID or the full post link (e.g., 4562 or https://t.me/c/123/4562): ").strip()
            try:
                if "/" in msg_id_input:
                    target_msg_id = int(msg_id_input.rstrip("/").split("/")[-1])
                else:
                    target_msg_id = int(msg_id_input)
            except ValueError:
                print("Invalid message ID format. Please enter a valid number or link.")
                continue

            print(f"\nFetching message {target_msg_id} directly...")
            message = await client.get_messages(current_channel, ids=target_msg_id)
            
            if not message:
                print(f"Could not find message ID {target_msg_id} in this chat.")
            else:
                downloaded = await download_message_media(message)
                if not downloaded:
                    print(f"Message {target_msg_id} does not contain any downloadable media.")
                    
        elif choice == "2":
            try:
                limit = int(input("\nHow many recent messages do you want to scan? (e.g. 50): "))
            except ValueError:
                limit = 50

            print("\nSearching for media...\n")
            media_count = 0
            async for message in client.iter_messages(current_channel, limit=limit):
                if message.media:
                    downloaded = await download_message_media(message)
                    if downloaded:
                        media_count += 1

            if media_count == 0:
                print("\nNo media found or downloaded in the scanned messages.")
            else:
                print(f"\n🎉 Finished scanning. {media_count} items processed. Saved in: {DOWNLOAD_DIR}")

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
