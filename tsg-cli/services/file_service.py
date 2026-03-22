import os
import time
import asyncio
from typing import List, Dict, Any
from pyrogram import Client
from utils.parser import extract_message_metadata, format_size
from utils.errors import TSGError
from utils.metadata_manager import get_custom_name

async def upload_file(client: Client, file_path: str) -> Dict[str, Any]:
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        raise TSGError("File not found. Please check the file path and try again.")

    try:
        if not client.is_connected:
            await client.connect()

        # Ensure client.me is populated
        if not getattr(client, "me", None):
            client.me = await client.get_me()

        is_premium = getattr(client.me, "is_premium", False)
        max_size = 4 * 1024 * 1024 * 1024 if is_premium else 2 * 1024 * 1024 * 1024

        file_size = os.path.getsize(abs_path)
        if file_size > max_size:
            limit_str = "4GB" if is_premium else "2GB"
            raise TSGError(f"File exceeds upload limit ({limit_str})")

        start_time = time.time()

        async def progress(current, total):
            elapsed = time.time() - start_time
            speed = current / elapsed if elapsed > 0 else 0
            speed_mb = speed / (1024 * 1024)

            c_fmt = format_size(current)
            t_fmt = format_size(total) if total > 0 else "?"

            if total > 0:
                percent = current * 100 / total
                print(f"\rUploading... {percent:.2f}% ({c_fmt}/{t_fmt}) | {speed_mb:.2f} MB/s", end="", flush=True)
            else:
                print(f"\rUploading... ({c_fmt}) | {speed_mb:.2f} MB/s", end="", flush=True)

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

def _is_internal_file(metadata: Dict[str, Any]) -> bool:
    name = metadata.get("name", "")
    caption = metadata.get("caption", "")
    return name == "metadata_backup.json" or "#TSG_METADATA_BACKUP" in caption

async def list_files(client: Client, limit: int = 50, sort_by: str = None, tag: str = None, page: int = 1, debug: bool = False) -> List[Dict[str, Any]]:
    # Enforce max limit = 200
    if limit > 200:
        limit = 200

    start = (page - 1) * limit
    end = start + limit

    tag = tag.lower().strip() if tag else None

    if debug:
        print(f"[DEBUG] list_files filters: tag='{tag}', sort_by='{sort_by}', limit={limit}, page={page}")

    files = []
    try:
        # Fetch newest first (default in Pyrogram)
        async for message in client.get_chat_history("me"):
            metadata = extract_message_metadata(message)
            if metadata:
                if debug:
                    print(f"[DEBUG] Raw metadata: {metadata}")

                # Hide internal files
                if _is_internal_file(metadata):
                    continue

                # Tag-based filtering (virtual folders)
                if tag:
                    raw_tags = metadata.get("tags") or []
                    if isinstance(raw_tags, str):
                        raw_tags = [t.strip() for t in raw_tags.split(",")] if raw_tags != "-" else []
                    tags_list = [t.lower() for t in raw_tags if t.strip()]

                    if tag not in tags_list:
                        continue

                files.append(metadata)
                if len(files) >= end:
                    break
    except Exception as e:
        raise Exception("Failed to list files. Please try again.")

    if sort_by == "date":
        files.sort(key=lambda x: x["date"], reverse=True)
    elif sort_by == "size":
        files.sort(key=lambda x: x["raw_size"], reverse=True)
    elif sort_by == "name":
        files.sort(key=lambda x: x["name"].lower())

    paginated_items = files[start:end]
    return paginated_items

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

        custom_name = get_custom_name(str(file_id))
        if custom_name:
            final_name = custom_name
        else:
            final_name = getattr(message.document or message.video or message.audio or message.photo, "file_name", metadata['name'])

        file_path = os.path.join(output_directory, final_name)

        # Start time is a list so we can mutate it in the closure during retries if needed,
        # or we just re-assign start_time before retry. Using a list is safer for closure scoping in python.
        time_tracker = [time.time()]

        async def progress(current, total):
            elapsed = time.time() - time_tracker[0]
            speed = current / elapsed if elapsed > 0 else 0
            speed_mb = speed / (1024 * 1024)

            c_fmt = format_size(current)
            t_fmt = format_size(total) if total > 0 else "?"

            if total > 0:
                percent = current * 100 / total
                print(f"\rDownloading... {percent:.2f}% ({c_fmt}/{t_fmt}) | {speed_mb:.2f} MB/s", end="", flush=True)
            else:
                print(f"\rDownloading... ({c_fmt}) | {speed_mb:.2f} MB/s", end="", flush=True)

        # Download the file
        try:
            downloaded_path = await client.download_media(message, file_name=file_path, progress=progress)
        except Exception as e:
            if "Peer id invalid" in str(e):
                chat = message.chat
                await client.get_chat(chat.id)
                print() # Ensure the next retry output is clean
                time_tracker[0] = time.time() # Reset start time for retry
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

def _matches_type(file_name: str, file_type: str) -> bool:
    ext = file_name.split(".")[-1].lower() if "." in file_name else ""
    if file_type == "video":
        return ext in ["mp4", "mkv", "avi"]
    elif file_type == "image":
        return ext in ["jpg", "jpeg", "png"]
    elif file_type == "document":
        return ext in ["pdf", "txt", "csv"]
    elif file_type == "audio":
        return ext in ["mp3", "wav", "ogg", "flac"]
    return False

async def search_files(client: Client, query: str, limit: int = 50, file_type: str = None, sort_by: str = None, tag: str = None, page: int = 1, debug: bool = False) -> List[Dict[str, Any]]:
    # Enforce max limit = 200
    if limit > 200:
        limit = 200

    start = (page - 1) * limit
    end = start + limit

    query = query.strip().lower() if query else None
    tag = tag.strip().lower() if tag else None
    file_type = file_type.strip().lower() if file_type else None

    if debug:
        print(f"[DEBUG] search_files filters: query='{query}', tag='{tag}', file_type='{file_type}', sort_by='{sort_by}', limit={limit}, page={page}")

    files = []
    try:
        # Fetch newest first (default in Pyrogram)
        async for message in client.get_chat_history("me"):
            if getattr(message, "empty", False) or getattr(message, "service", False):
                continue

            metadata = extract_message_metadata(message)
            if not metadata:
                continue

            if debug:
                print(f"[DEBUG] Raw metadata: {metadata}")

            file_name = metadata.get("name", "").lower()

            # Hide internal files
            if _is_internal_file(metadata):
                continue

            # AND logic: Name-based filtering
            if query and query not in file_name:
                continue

            # AND logic: Tag-based filtering
            if tag:
                raw_tags = metadata.get("tags") or []
                if isinstance(raw_tags, str):
                    raw_tags = [t.strip() for t in raw_tags.split(",")] if raw_tags != "-" else []
                tags_list = [t.lower() for t in raw_tags if t.strip()]

                if tag not in tags_list:
                    continue

            # AND logic: Type-based filtering (using extension fallback to mimic Pyrogram attributes safely)
            if file_type:
                # Also double check Pyrogram native types as a primary source if they exist
                has_native = False
                if file_type == "video" and getattr(message, "video", None): has_native = True
                elif file_type == "image" and getattr(message, "photo", None): has_native = True
                elif file_type == "document" and getattr(message, "document", None): has_native = True
                elif file_type == "audio" and getattr(message, "audio", None): has_native = True

                # If neither native Pyrogram type matches nor extension matches, skip
                if not has_native and not _matches_type(file_name, file_type):
                    continue

            files.append(metadata)
            if len(files) >= end:
                break
    except Exception as e:
        raise Exception("Failed to search files. Please try again.")

    if sort_by == "date":
        files.sort(key=lambda x: x["date"], reverse=True)
    elif sort_by == "size":
        files.sort(key=lambda x: x["raw_size"], reverse=True)
    elif sort_by == "name":
        files.sort(key=lambda x: x["name"].lower())

    paginated_items = files[start:end]
    return paginated_items
