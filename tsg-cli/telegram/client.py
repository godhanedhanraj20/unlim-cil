from pyrogram import Client
from utils.config_manager import load_config, SESSION_FILE

def get_client(api_id: int, api_hash: str) -> Client:
    """Returns a Pyrogram client configured with the given credentials."""
    return Client(
        name=SESSION_FILE,
        api_id=api_id,
        api_hash=api_hash,
        no_updates=True
    )
