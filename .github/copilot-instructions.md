# Zion Discord Bot - Copilot Instructions

## Project Overview
This is a Discord music bot built with Python 3.13 using discord.py, yt-dlp, and FFmpeg. The bot streams audio from YouTube without downloading files, with per-guild queue management and graceful shutdown handling.

## Architecture & Key Components

### Core Structure
- **Entry Point**: `src/bot.py` - Creates bot instance, loads cogs, handles signals
- **Configuration**: `src/config.py` - Environment variables and YTDL/FFmpeg options
- **Music Engine**: `src/core/ytdl.py` - YouTube streaming with `YTDLSource` class
- **Command System**: `src/cogs/music.py` - All music commands as discord.py cog
- **Logging**: `src/logger.py` - Loguru configuration with colored output

### Queue Management Pattern
The bot uses per-guild `deque` queues stored in `Music.queues[guild_id]`. Key pattern:
- `play_next()` is called recursively via FFmpeg's `after` callback
- Queue state is logged extensively for debugging
- Voice channel validation happens in `ensure_voice()` before_invoke hook

### Voice Connection Flow
1. User must be in voice channel
2. Bot connects via `ensure_voice()` method 
3. Rigid validation: bot and user must be in same channel
4. Graceful disconnect on shutdown via `core/shutdown.py`

## Development Patterns

### Command Structure
All music commands follow this pattern:
```python
@commands.command()
async def command_name(self, ctx):
    # Voice client validation
    if not ctx.voice_client or not ctx.voice_client.is_connected():
        await ctx.send("❌ Bot is not connected to a voice channel.")
        return
    # Command logic with emoji feedback
```

### Error Handling
- Extensive logging with loguru at DEBUG/INFO/ERROR levels
- User-friendly emoji messages (❌, ✅, 🎶, ⏭️, etc.)
- Exception catching in async methods with context feedback

### Audio Processing
- `YTDLSource.from_url()` for direct YouTube URLs
- `YTDLSource.from_string()` for search queries (uses `ytsearch:` prefix)
- All streaming uses `stream=True` - no file downloads
- FFmpeg options include reconnection and buffering for stability

## Development Workflows

### Local Development
```bash
# Environment setup (create .env with DISCORD_TOKEN)
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run bot
python src/bot.py
```

### Docker Workflow  
```bash
# Build and push (requires version)
./build.sh 1.0.1

# Run with compose
docker-compose up -d
```

### Testing
- Unit tests in `tests/` focus on voice channel state validation
- Mock discord.py objects extensively
- Test queue management and error conditions
- Run with: `pytest tests/`

## Critical Implementation Details

### Signal Handling
The bot uses proper asyncio signal handling for graceful shutdown:
- Disconnects all voice clients before closing
- Uses `bot.should_exit` flag to coordinate shutdown
- Signal handlers registered in `main()` function

### YouTube Integration  
- Uses yt-dlp (not youtube-dl) for better format support
- Search queries automatically prefixed with `ytsearch:`
- URL detection via regex in `is_youtube_url()`
- PCMVolumeTransformer for volume control

### Deployment
- Multi-stage Docker build optimized for Python 3.13
- Environment variables passed via docker-compose
- Uses restart: unless-stopped for reliability
- Images pushed to Docker Hub as `ibfleming/zion-discord-bot`

## Important Gotchas
- Bot requires message content intent to read commands
- Voice connections are persistent - validate state before commands
- Queue playback relies on FFmpeg `after` callback - don't break this chain
- All async commands need proper exception handling for user feedback
- YTDL format options are critical for streaming stability
