# Tibia Discord Bot

## Overview

This is a Discord bot that intelligently tracks and posts daily boosted creatures and bosses from the MMORPG Tibia. The bot automatically monitors changes to the daily boosted creature and boss, posting updates only when they actually change to prevent spam. It uses the TibiaData API v4 for accurate data and posts at 10:06 CEST (right after Tibia server boot). The bot features custom skull and sword branding and is designed for easy deployment to Railway.com.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture
- **Language**: Python 3.11+
- **Framework**: discord.py for Discord API integration
- **API Integration**: TibiaData API v4 for game data
- **Scheduling**: APScheduler for automated daily checks
- **Deployment**: Designed for Railway deployment with environment variable configuration

### Component Structure
The bot follows a modular architecture with separate components:
- `main.py`: Entry point and bot initialization
- `bot/`: Core bot functionality split into specialized modules
- `bot/tibia_api.py`: API client for TibiaData
- `bot/embed_builder.py`: Discord embed creation and formatting
- `bot/scheduler.py`: Task scheduling with timezone awareness

## Key Components

### TibiaBot Class (main.py)
- Extends discord.py's commands.Bot
- Manages bot configuration and component initialization
- Handles Discord intents and command prefix
- Coordinates between API, scheduler, and embed builder
- Registers all slash commands for user interaction

### TibiaAPI (bot/tibia_api.py)
- Handles all HTTP requests to TibiaData API v4
- Implements connection pooling with aiohttp
- Provides retry logic for failed requests
- Manages session lifecycle and cleanup
- **NEW**: Fallback to TibiaWiki scraping when TibiaData API fails
- **NEW**: HTML parsing for creature information extraction
- **NEW**: Graceful degradation with fallback creature data

### EmbedBuilder (bot/embed_builder.py)
- Creates rich Discord embeds for creature and boss announcements
- Handles color schemes and custom skull/sword branding
- Integrates creature images from TibiaWiki
- Formats creature stats and information
- Uses custom icon URL for consistent branding across all embeds

### TibiaScheduler (bot/scheduler.py)
- Manages automated daily checks using APScheduler
- Handles Central European timezone (CET/CEST) awareness
- Schedules primary check at 10:06 and backup check 30 minutes later
- Prevents duplicate executions with job coalescing

## Data Flow

1. **Scheduled Trigger**: At 10:06 CEST daily, scheduler triggers boosted creature/boss check
2. **API Request**: TibiaAPI fetches current boosted data from TibiaData API
3. **Change Detection**: Bot compares current data with previously posted data
4. **Embed Creation**: If changes detected, EmbedBuilder creates formatted Discord embeds
5. **Channel Posting**: Bot posts embeds to configured Discord channels
6. **State Update**: Bot updates internal state to track last posted creatures/bosses

## External Dependencies

### APIs
- **TibiaData API v4**: Primary data source for boosted creatures and bosses
- **Discord API**: Bot communication via discord.py library
- **TibiaWiki**: Image URLs for creature thumbnails

### Python Libraries
- **discord.py**: Discord bot framework
- **aiohttp**: Async HTTP client for API requests
- **apscheduler**: Task scheduling
- **pytz**: Timezone handling
- **python-dotenv**: Environment variable management

## Deployment Strategy

### Railway Deployment (Recommended)
- One-click deployment via Railway template
- Environment variables for configuration
- Automatic scaling and monitoring
- Built-in logging and health checks

### Environment Variables
- `DISCORD_TOKEN`: Discord bot authentication token
- `CREATURE_CHANNEL_ID`: Discord channel ID for boosted creature posts
- `BOSS_CHANNEL_ID`: Discord channel ID for boosted boss posts

### Configuration Requirements
- Discord bot must have permissions to send messages and embed links
- Channels must be accessible to the bot
- Bot requires message content intent for command handling

### Monitoring and Logging
- File-based logging (`bot.log`) and console output
- Comprehensive error handling and retry logic
- Grace periods for missed scheduled jobs
- Session management for long-running connections

## Recent Changes: Latest modifications with dates

### July 18, 2025
- **FIXED**: API endpoint bug - creatures now correctly detected using /v4/creatures instead of /v4/world/Antica
- **ENHANCED**: Added /creature and /boss commands with detailed information
- **ADDED**: /next command - shows next server save countdown
- **ADDED**: /schedule command - shows bot's posting schedule
- **IMPROVED**: Multi-source data strategy (TibiaData API + TibiaWiki fallback)
- **IMPROVED**: Better error handling and logging for data source tracking