# ZION Discord Music Bot

A powerful Discord music bot built with Python 3.13 that streams high-quality audio directly from YouTube without downloading files. Features per-guild queue management, seamless playback, and graceful shutdown handling.

## Features

- **YouTube Streaming**: Direct audio streaming from YouTube using yt-dlp
- **Per-Guild Queues**: Independent music queues for each Discord server
- **High Performance**: Built with discord.py 2.6 and asyncio for optimal performance
- **Complete Playback Controls**: Play, pause, resume, skip, stop, and volume control
- **Smart Queue Management**: Add, view, and clear queues with ease
- **High-Quality Audio**: FFmpeg integration with reconnection and buffering
- **Robust Error Handling**: Comprehensive logging and graceful error recovery
- **Docker Ready**: Containerized deployment with multi-stage builds

## Commands

All commands use the `.` prefix:

### Music Playback

| Command | Description | Example |
|---------|-------------|---------|
| `.play <url or search>` | Play a song or add it to the queue | `.play never gonna give you up` |
| `.pause` | Pause the current song | `.pause` |
| `.resume` | Resume the paused song | `.resume` |
| `.skip` | Skip to the next song in the queue | `.skip` |
| `.stop` | Stop playback and disconnect from voice | `.stop` |
| `.volume <0-100>` | Set playback volume (0-100%) | `.volume 75` |

### Queue Management

| Command | Description | Example |
|---------|-------------|---------|
| `.queue list` | Show the current queue | `.queue list` |
| `.queue add <song>` | Add a song to the queue | `.queue add bohemian rhapsody` |
| `.queue clear` | Clear the entire queue | `.queue clear` |

### General

| Command | Description |
|---------|-------------|
| `.help` | Show available commands |

## Quick Start

### Prerequisites

- Python 3.13+
- FFmpeg installed and available in PATH
- Discord Bot Token

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ibfleming/zion-discord-bot.git
   cd zion-discord-bot
   ```

2. **Set up environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   # Create .env file
   echo "DISCORD_TOKEN=your_discord_bot_token_here" > .env
   ```

4. **Run the bot:**
   ```bash
   python src/bot.py
   ```

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Create environment file:**
   ```bash
   echo "DISCORD_TOKEN=your_discord_bot_token_here" > .env
   ```

2. **Deploy with compose:**
   ```bash
   docker-compose up -d
   ```

### Manual Docker Build

1. **Build and run:**
   ```bash
   ./build.sh 1.0.1
   docker run -d --name zion-bot -e DISCORD_TOKEN=your_token ibfleming/zion-discord-bot:latest
   ```

## Development

### Project Structure

```plaintext
src/
├── bot.py          # Main entry point and bot setup
├── config.py       # Configuration and environment variables  
├── logger.py       # Logging configuration
├── cogs/
│   ├── music.py    # Music commands and queue management
│   └── help.py     # Help command
├── core/
│   ├── ytdl.py     # YouTube streaming engine
│   └── shutdown.py # Graceful shutdown handling
└── utils/
    └── terminal.py # Terminal configuration
```

### Running Tests
```bash
pytest tests/
```

### Key Technologies
- **discord.py 2.6**: Discord API wrapper with voice support
- **yt-dlp**: YouTube audio extraction and streaming
- **FFmpeg**: Audio processing and streaming
- **loguru**: Advanced logging with colors and formatting
- **asyncio**: Asynchronous programming for high performance

## Configuration

The bot uses environment variables for configuration:

- `DISCORD_TOKEN`: Your Discord bot token (required)

FFmpeg and yt-dlp options are pre-configured for optimal streaming performance.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
