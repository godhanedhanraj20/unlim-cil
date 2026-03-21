import os
import asyncio
from typing import List, Dict, Any
from pyrogram import Client
from utils.parser import extract_message_metadata
from utils.errors import TSGError

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024 # 2GB

async def upload_file(client: Client, file_path: str) -> Dict[str, Any]:
    if not os.path.exists(file_path):
        raise TSGError("File not found. Please check the file path and try again.")

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise TSGError("File exceeds 2GB limit. Cannot upload.")

    try:
        message = await client.send_document("me", document=file_path)
        metadata = extract_message_metadata(message)
        if not metadata:
            raise TSGError("Failed to extract metadata after upload.")
        return metadata
    except Exception as e:
        if isinstance(e, TSGError):
            raise e
        raise Exception("Upload failed. Please try again.")

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

        # Download the file
        downloaded_path = await client.download_media(message, file_name=file_path)
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
