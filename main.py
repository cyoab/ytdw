#!/usr/bin/env python3
"""YouTube video downloader CLI tool."""

import argparse
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)
import yt_dlp

console = Console()


def get_default_output_dir() -> Path:
    """Get the default output directory (Windows Videos/Youtube Downloads on WSL)."""
    # Try to get Windows username from WSL
    try:
        result = subprocess.run(
            ["cmd.exe", "/c", "echo %USERNAME%"],
            capture_output=True,
            text=True,
            check=True,
        )
        win_username = result.stdout.strip()
        win_videos = Path(f"/mnt/c/Users/{win_username}/Videos/Youtube Downloads")
        return win_videos
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to home directory if not on WSL or cmd.exe not available
        return Path.home() / "Youtube Downloads"


def download_video(url: str, output_dir: Path, skip_thumbnail: bool = False) -> bool:
    """Download a YouTube video to the specified directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(output_dir / "%(title)s.%(ext)s")

    # First, fetch video info
    info_opts = {
        "quiet": True,
        "no_warnings": True,
        "js_runtimes": {"bun": {}},
    }

    try:
        console.print(Panel("[bold blue]Fetching video info...[/bold blue]", border_style="blue"))

        with yt_dlp.YoutubeDL(info_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        console.print(Panel(
            f"[bold]{info.get('title', 'Unknown')}[/bold]\n"
            f"[dim]Channel:[/dim] {info.get('uploader', 'Unknown')}\n"
            f"[dim]Duration:[/dim] {info.get('duration_string', 'Unknown')}",
            title="Video Info",
            border_style="green"
        ))

    except Exception as e:
        console.print(Panel(f"[red bold]Failed to fetch video info:[/red bold]\n{e}", border_style="red"))
        return False

    # Now download with progress bar
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(bar_width=40),
        "[progress.percentage]{task.percentage:>3.1f}%",
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,
    )

    task_id = None
    current_filename = "video"

    def progress_hook(d: dict):
        nonlocal task_id, current_filename

        if d["status"] == "downloading":
            filename = Path(d.get("filename", "video")).name

            # Get total and downloaded bytes
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)

            if task_id is None and total > 0:
                current_filename = filename
                task_id = progress.add_task(f"Downloading", total=total)
                progress.start()

            if task_id is not None:
                progress.update(task_id, completed=downloaded)

        elif d["status"] == "finished":
            if task_id is not None:
                progress.update(task_id, completed=progress.tasks[task_id].total)
            console.print("[green]✓[/green] Download complete, processing...")

        elif d["status"] == "error":
            console.print("[red]✗[/red] Download failed")

    ydl_opts = {
        "outtmpl": output_template,
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
        # Format selection - best video+audio, fallback to pre-merged or best available
        "format": "bv*+ba/b/22/18/best",
        "merge_output_format": "mp4",
        # Use bun as JS runtime for YouTube signature decryption
        "js_runtimes": {"bun": {}},
        # Also download thumbnail (unless --no-thumbnail is specified)
        "writethumbnail": not skip_thumbnail,
        # Retry on failure
        "retries": 3,
        "fragment_retries": 3,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        },
    }

    try:
        with progress:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        console.print(Panel(
            f"[green bold]✓ Video saved to:[/green bold]\n{output_dir}",
            border_style="green"
        ))
        return True

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "ffmpeg" in error_msg.lower() or "merge" in error_msg.lower():
            console.print(Panel(
                "[red bold]Download Error:[/red bold]\n"
                f"{e}\n\n"
                "[yellow]Hint:[/yellow] Install ffmpeg to merge video/audio streams:\n"
                "  sudo apt install ffmpeg",
                border_style="red"
            ))
        else:
            console.print(Panel(f"[red bold]Download Error:[/red bold]\n{e}", border_style="red"))
        return False
    except Exception as e:
        console.print(Panel(f"[red bold]Error:[/red bold]\n{e}", border_style="red"))
        return False


def download_thumbnail(url: str, output_dir: Path) -> bool:
    """Download only the thumbnail of a YouTube video."""
    output_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(output_dir / "%(title)s.%(ext)s")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "writethumbnail": True,
        "outtmpl": output_template,
        "js_runtimes": {"bun": {}},
    }

    try:
        console.print(Panel("[bold blue]Fetching thumbnail...[/bold blue]", border_style="blue"))

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        console.print(Panel(
            f"[bold]{info.get('title', 'Unknown')}[/bold]\n"
            f"[dim]Channel:[/dim] {info.get('uploader', 'Unknown')}",
            title="Video Info",
            border_style="green"
        ))

        console.print(Panel(
            f"[green bold]✓ Thumbnail saved to:[/green bold]\n{output_dir}",
            border_style="green"
        ))
        return True

    except Exception as e:
        console.print(Panel(f"[red bold]Error downloading thumbnail:[/red bold]\n{e}", border_style="red"))
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube videos with style",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "url",
        help="YouTube video URL to download",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output directory (default: Windows Videos/Youtube Downloads)",
    )
    parser.add_argument(
        "--thumbnail",
        action="store_true",
        help="Download only the thumbnail (skip video download)",
    )
    parser.add_argument(
        "--no-thumbnail",
        action="store_true",
        dest="no_thumbnail",
        help="Skip downloading the thumbnail with the video",
    )

    args = parser.parse_args()

    output_dir = args.output if args.output else get_default_output_dir()

    console.print(Panel(
        "[bold magenta]ytdw[/bold magenta] - YouTube Downloader",
        border_style="magenta"
    ))

    if args.thumbnail:
        success = download_thumbnail(args.url, output_dir)
    else:
        success = download_video(args.url, output_dir, skip_thumbnail=args.no_thumbnail)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
