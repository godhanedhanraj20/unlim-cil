from utils.metadata_manager import get_tags

def format_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB")
    i = 0
    p = size_bytes
    while p >= 1024 and i < len(size_name) - 1:
        p /= 1024.0
        i += 1
    return f"{p:.2f} {size_name[i]}"

def extract_message_metadata(message):
    """
    Extracts metadata from a Pyrogram message.
    Returns None if the message doesn't contain a valid media type.
    """
    if not message:
        return None

    # Skip empty messages or service messages safely
    if getattr(message, "empty", False) or getattr(message, "service", False):
        return None

    media = None
    media_type = None

    # Check for valid media types using getattr to avoid errors on unexpected objects
    if getattr(message, "document", None):
        media = message.document
        media_type = "document"
    elif getattr(message, "video", None):
        media = message.video
        media_type = "video"
    elif getattr(message, "audio", None):
        media = message.audio
        media_type = "audio"
    elif getattr(message, "photo", None):
        media = message.photo
        media_type = "photo"

    if not media:
        return None

    # Get file name
    file_name = getattr(media, "file_name", None)
    if not file_name:
        file_name = f"file_{message.id}"
        if media_type == "photo":
            file_name += ".jpg"
        elif media_type == "video":
            file_name += ".mp4"
        elif media_type == "audio":
            file_name += ".mp3"

    # Get file size
    file_size = getattr(media, "file_size", 0)
    formatted_size = format_size(file_size)

    # Get date
    date = message.date.strftime("%Y-%m-%d %H:%M:%S") if getattr(message, "date", None) else "Unknown"

    # Get tags
    tags = get_tags(str(message.id))
    formatted_tags = ", ".join(tags) if tags else "-"

    return {
        "id": message.id,
        "name": file_name,
        "size": formatted_size,
        "date": date,
        "tags": formatted_tags,
        "raw_size": file_size
    }
