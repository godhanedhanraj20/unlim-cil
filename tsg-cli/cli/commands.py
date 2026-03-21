import asyncio
import typer
from rich.console import Console
from rich.table import Table
import os

from services.auth import interactive_login, get_authenticated_client
from services.file_service import upload_file, list_files, download_file, delete_file
from utils.errors import TSGError

app = typer.Typer(help="TSG-CLI: Telegram Storage CLI")
console = Console()

def run_async(coro):
    try:
        return asyncio.run(coro)
    except TSGError as e:
        console.print(f"[red]{str(e)}[/red]")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red][DEBUG] {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def login():
    """Authenticate with Telegram using OTP."""
    run_async(interactive_login())

@app.command()
def upload(file_path: str = typer.Argument(..., help="Path to the file to upload")):
    """Upload a file to Telegram Saved Messages."""
    async def _upload():
        client = await get_authenticated_client()
        try:
            console.print(f"[cyan]Uploading {file_path}...[/cyan]")
            metadata = await upload_file(client, file_path)
            console.print("[green]Upload successful[/green]")
            console.print(f"Message ID: {metadata['id']}")
            console.print(f"File name: {metadata['name']}")
            console.print(f"File size: {metadata['size']}")
        finally:
            await client.disconnect()

    run_async(_upload())

@app.command(name="list")
def list_cmd(limit: int = typer.Option(50, "--limit", "-l", help="Number of files to list (max 200)")):
    """List files stored in Telegram Saved Messages."""
    async def _list():
        client = await get_authenticated_client()
        try:
            console.print("[cyan]Fetching files...[/cyan]")
            files = await list_files(client, limit)

            if not files:
                console.print("[yellow]No files found in Saved Messages.[/yellow]")
                return

            table = Table(title="Stored Files")
            table.add_column("ID", justify="left", style="cyan", no_wrap=True)
            table.add_column("Name", style="magenta")
            table.add_column("Size", justify="right", style="green")
            table.add_column("Date", style="blue")

            for f in files:
                table.add_row(str(f["id"]), f["name"], f["size"], f["date"])

            console.print(table)
        finally:
            await client.disconnect()

    run_async(_list())

@app.command()
def download(
    file_id: int = typer.Argument(..., help="ID of the file to download"),
    output: str = typer.Option(".", "--output", "-o", help="Output directory path")
):
    """Download a file by ID."""
    async def _download():
        client = await get_authenticated_client()
        try:
            console.print(f"[cyan]Downloading file {file_id}...[/cyan]")
            path = await download_file(client, file_id, output)
            console.print(f"[green]Downloaded to: {path}[/green]")
        finally:
            await client.disconnect()

    run_async(_download())

@app.command()
def delete(file_id: int = typer.Argument(..., help="ID of the file to delete")):
    """Delete a file by ID."""
    async def _delete():
        client = await get_authenticated_client()
        try:
            confirm = typer.confirm(f"Are you sure you want to delete file ID {file_id}?")
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return

            console.print(f"[cyan]Deleting file {file_id}...[/cyan]")
            await delete_file(client, file_id)
            console.print("[green]File deleted successfully![/green]")
        finally:
            await client.disconnect()

    run_async(_delete())

if __name__ == "__main__":
    app()
