# 🎬 ytdw - YouTube Downloader

A simple CLI tool to download YouTube videos with a clean, colorful terminal interface. ✨

## 📋 Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- **bun** - JavaScript runtime required for YouTube signature decryption
- **ffmpeg** - required for merging video/audio streams (for best quality)
- WSL (Windows Subsystem for Linux) - optional, for default Windows path support

## 🚀 Installation

```bash
# Install ffmpeg (required for video/audio merging)
# Ubuntu/Debian/WSL:
sudo apt install ffmpeg

# Clone the repository
git clone <repository-url>
cd ytdw

# Install dependencies
uv sync
```

## 📖 Usage

```bash
# Download a video to the default location (Windows Videos/Youtube Downloads)
uv run main.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Download to a specific directory
uv run main.py "https://www.youtube.com/watch?v=VIDEO_ID" -o /path/to/directory

# Download only the thumbnail (skip video)
uv run main.py "https://www.youtube.com/watch?v=VIDEO_ID" --thumbnail

# Download video without thumbnail
uv run main.py "https://www.youtube.com/watch?v=VIDEO_ID" --no-thumbnail

# Show help
uv run main.py --help
```

### ⚙️ Arguments

| Argument | Description |
|----------|-------------|
| `url` | YouTube video URL to download (required) |
| `-o, --output` | Output directory (default: `C:\Users\<username>\Videos\Youtube Downloads` on WSL, or `~/Youtube Downloads` on Linux) |
| `--thumbnail` | Download only the thumbnail image (skips video download) 🖼️ |
| `--no-thumbnail` | Skip downloading the thumbnail with the video 🚫🖼️ |

## ✅ Features

- 🎥 Downloads YouTube videos in best available quality
- 📝 Displays video info (title, channel, duration) before downloading
- 📊 Shows real-time download progress with speed and ETA
- 🖼️ Automatically saves video thumbnails
- 🪟 Automatically detects Windows Videos folder when running on WSL
- 🌈 Colorful terminal output using Rich
