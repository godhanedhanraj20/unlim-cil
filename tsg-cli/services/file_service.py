import os
import asyncio
from typing import List, Dict, Any
from pyrogram import Client
from utils.parser import extract_message_metadata
from utils.errors import TSGError

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024 # 2GB

async def upload_file(client: Client, file_path: str) -> Dict[str, Any]:
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        raise TSGError("File not found. Please check the file path and try again.")

    file_size = os.path.getsize(abs_path)
    if file_size > MAX_FILE_SIZE:
        raise TSGError("File exceeds 2GB limit. Cannot upload.")

    async def progress(current, total):
        if total > 0:
            percent = current * 100 / total
            print(f"\rUploading... {percent:.2f}% ({current}/{total})", end="", flush=True)
        else:
            print(f"\rUploading... ({current} bytes)", end="", flush=True)

    try:
        if not client.is_connected:
            await client.connect()

        message = await client.send_document("me", document=abs_path, progress=progress)
        print() # Move to next line after upload finishes

        metadata = extract_message_metadata(message)
        if not metadata:
            raise TSGError("Failed to extract metadata after upload.")
        return metadata
    except Exception as e:
        print() # Ensure the next line is clean if it fails mid-upload
        if isinstance(e, TSGError):
            raise e
        raise TSGError(f"Upload failed: {str(e)}")

async def list_files(client: Client, limit: int = 50) -> List[Dict[str, Any]]:
    # Enforce max limit = 200
    if limit > 200:
        limit = 200

    files = []
    try:
        # Fetch newest first (default in Pyrogram)
        async for message in client.get_chat_history("me"):
            metadata = extract_message_metadata(message)
            if metadata:
                files.append(metadata)
                if len(files) >= limit:
                    break
    except Exception as e:
        raise Exception("Failed to list files. Please try again.")

    return files

async def download_file(client: Client, file_id: int, output_directory: str) -> str:
    if not os.path.exists(output_directory):
        raise TSGError("Output directory not found. Please check the directory path and try again.")

    if not os.path.isdir(output_directory):
        raise TSGError("Path is not a directory. Please provide a valid directory path.")

    try:
        # get_messages returns a single message if passed a single ID
        message = await client.get_messages("me", file_id)
        if not message or getattr(message, "empty", False):
            raise TSGError(f"File with ID {file_id} not found.")

        metadata = extract_message_metadata(message)
        if not metadata:
            raise TSGError(f"Message ID {file_id} does not contain valid media.")

        file_path = os.path.join(output_directory, metadata['name'])

        async def progress(current, total):
            if total > 0:
                percent = current * 100 / total
                print(f"\rDownloading... {percent:.2f}% ({current}/{total})", end="", flush=True)
            else:
                print(f"\rDownloading... ({current} bytes)", end="", flush=True)

        # Download the file
        try:
            downloaded_path = await client.download_media(message, file_name=file_path, progress=progress)
        except Exception as e:
            if "Peer id invalid" in str(e):
                chat = message.chat
                await client.get_chat(chat.id)
                print() # Ensure the next retry output is clean
                downloaded_path = await client.download_media(message, file_name=file_path, progress=progress)
            else:
                raise

        print()  # after download finishes
        if not downloaded_path:
            raise TSGError("Download failed, received empty path from Telegram.")

        return downloaded_path
    except TSGError as e:
        raise e
    except Exception as e:
        raise Exception("Download failed. Please try again.")

async def delete_file(client: Client, file_id: int):
    try:
        message = await client.get_messages("me", file_id)
        if not message or getattr(message, "empty", False):
            raise TSGError(f"File with ID {file_id} not found.")

        metadata = extract_message_metadata(message)
        if not metadata:
            raise TSGError(f"Message ID {file_id} does not contain valid media.")

        await client.delete_messages("me", file_id)
    except TSGError as e:
        raise e
    except Exception as e:
        raise Exception("Delete failed. Please try again.")

async def search_files(client: Client, query: str, limit: int = 50) -> List[Dict[str, Any]]:
    # Enforce max limit = 200
    if limit > 200:
        limit = 200

    query = query.strip().lower()
    if not query:
        raise TSGError("Search query cannot be empty.")

    files = []
    try:
        # Fetch newest first (default in Pyrogram)
        async for message in client.get_chat_history("me"):
            metadata = extract_message_metadata(message)
            if metadata:
                # Filter by filename matching query
                if query in metadata['name'].lower():
                    files.append(metadata)
                    if len(files) >= limit:
                        break
    except Exception as e:
        raise Exception("Failed to search files. Please try again.")

    return files
