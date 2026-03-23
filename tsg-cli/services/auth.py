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
    try:
        await client.connect()
    except Exception:
        await client.disconnect()
        await client.connect()

    try:
        try:
            me = await client.get_me()
            if me:
                console.print("[green]Already logged in![/green]")
                if getattr(me, "is_premium", False):
                    console.print("[green]Premium account detected — 4GB upload limit[/green]")
                else:
                    console.print("[yellow]Free account — 2GB upload limit[/yellow]")
                return
        except Exception:
            pass # Not logged in

        phone_number = typer.prompt("Enter your phone number (e.g., +1234567890)")

        try:
            sent_code = await client.send_code(phone_number)
        except Exception as e:
            console.print(f"[red]Error sending code: {str(e)}[/red]")
            raise TSGError(str(e))

        phone_code = typer.prompt("Enter the OTP code received on Telegram")

        try:
            await client.sign_in(phone_number, sent_code.phone_code_hash, phone_code)
        except SessionPasswordNeeded:
            password = typer.prompt("Two-Step Verification enabled. Enter your password", hide_input=True)
            try:
                await client.check_password(password)
            except Exception as e:
                console.print(f"[red]Invalid password: {str(e)}[/red]")
                raise TSGError(str(e))
        except (PhoneCodeInvalid, PhoneCodeExpired) as e:
            console.print(f"[red]Invalid or expired code: {str(e)}[/red]")
            raise TSGError(str(e))
        except Exception as e:
            console.print(f"[red]Failed to sign in: {str(e)}[/red]")
            raise TSGError(str(e))

        console.print("[green]Successfully logged in![/green]")

        # Show limit logic on fresh login
        try:
            me = await client.get_me()
            if getattr(me, "is_premium", False):
                console.print("[green]Premium account detected — 4GB upload limit[/green]")
            else:
                console.print("[yellow]Free account — 2GB upload limit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error fetching limits: {str(e)}[/red]")

    finally:
        await client.disconnect()

async def get_authenticated_client() -> Client:
    config = load_config()
    api_id = config.get("api_id")
    api_hash = config.get("api_hash")
    if not api_id or not api_hash:
        raise TSGError("You are not logged in. Run: python main.py login")

    client = get_client(api_id, api_hash)
    try:
        await client.connect()
        user = await client.get_me()
        client.me = user  # Fix: Ensure Pyrogram internal state is fully initialized

        if not user:
            await client.disconnect()
            raise TSGError("Authentication failed. Please login again.")
        return client
    except Exception as e:
        if isinstance(e, TSGError):
            raise e
        if "login" in str(e).lower():
            raise TSGError("You are not logged in. Run: python main.py login")
        raise TSGError("You are not logged in. Run: python main.py login")
