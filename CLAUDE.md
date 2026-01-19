# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ytdw is a YouTube video downloader CLI tool. Python 3.12 project managed with `uv`, running on WSL (Windows 11).

**Key dependencies:**
- `yt-dlp` - YouTube video downloading
- `rich` - Terminal UI and formatting

## Commands

```bash
# Download a video (default: Windows Videos/Youtube Downloads)
uv run main.py "https://youtube.com/watch?v=VIDEO_ID"

# Download to specific directory
uv run main.py "https://youtube.com/watch?v=VIDEO_ID" -o /path/to/dir

# Dependency management
uv add <package>
uv add --dev <package>
uv sync
```

## Architecture

Entry point: `main.py`

- `get_default_output_dir()` - Detects Windows Videos folder via WSL's cmd.exe, falls back to ~/Youtube Downloads
- `download_video(url, output_dir)` - Downloads video using yt-dlp with Rich progress display
- `main()` - CLI argument parsing with argparse
