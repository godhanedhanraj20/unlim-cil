import asyncio
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired
import typer
from rich.console import Console
import os

from utils.config_manager import load_config, save_config, SESSION_FILE
from telegram.client import get_client
from utils.errors import TSGError

console = Console()

async def interactive_login():
    config = load_config()

    api_id = config.get("api_id")
    api_hash = config.get("api_hash")

    if not api_id or not api_hash:
        console.print("[yellow]First time setup: Enter your Telegram API credentials.[/yellow]")
        console.print("You can get these from https://my.telegram.org/apps")
        api_id = typer.prompt("API ID", type=int)
        api_hash = typer.prompt("API Hash", type=str)
        config["api_id"] = api_id
        config["api_hash"] = api_hash
        save_config(config)

    client = get_client(api_id, api_hash)

    console.print("[cyan]Connecting to Telegram...[/cyan]")
    await client.connect()

    try:
        me = await client.get_me()
        if me:
            console.print("[green]Already logged in![/green]")
            await client.disconnect()
            return
    except Exception:
        pass # Not logged in

    phone_number = typer.prompt("Enter your phone number (e.g., +1234567890)")

    try:
        sent_code = await client.send_code(phone_number)
    except Exception as e:
        console.print("[red]Error sending code. Please try again.[/red]")
        await client.disconnect()
        return

    phone_code = typer.prompt("Enter the OTP code received on Telegram")

    try:
        await client.sign_in(phone_number, sent_code.phone_code_hash, phone_code)
    except SessionPasswordNeeded:
        password = typer.prompt("Two-Step Verification enabled. Enter your password", hide_input=True)
        try:
            await client.check_password(password)
        except Exception as e:
            console.print("[red]Invalid password. Please try again.[/red]")
            await client.disconnect()
            return
    except (PhoneCodeInvalid, PhoneCodeExpired) as e:
        console.print("[red]Invalid or expired code. Please try again.[/red]")
        await client.disconnect()
        return
    except Exception as e:
        console.print("[red]Failed to sign in. Please try again.[/red]")
        await client.disconnect()
        return

    console.print("[green]Successfully logged in![/green]")
    await client.disconnect()

async def get_authenticated_client() -> Client:
    config = load_config()
    api_id = config.get("api_id")
    api_hash = config.get("api_hash")
    if not api_id or not api_hash:
        raise TSGError("You are not logged in. Run: python main.py login")

    client = get_client(api_id, api_hash)
    try:
        session_path = os.path.expanduser("~/.tsg-cli/session.session")
        print(f"[DEBUG] Session file exists: {os.path.exists(session_path)}")
        print(f"[DEBUG] Client object: {client}")
        print("[DEBUG] Initializing client")
        await client.connect()
        print(f"[DEBUG] Client connected: {client.is_connected}")

        user = await client.get_me()
        print(f"[DEBUG] get_me() result: {user}")

        if user:
            print(f"[DEBUG] User ID: {user.id}")
            print(f"[DEBUG] User is_premium: {getattr(user, 'is_premium', None)}")
        else:
            await client.disconnect()
            raise TSGError("Authentication failed. Please login again.")
        return client
    except Exception as e:
        if isinstance(e, TSGError):
            raise e
        if "login" in str(e).lower():
            raise TSGError("You are not logged in. Run: python main.py login")
        raise TSGError("You are not logged in. Run: python main.py login")
