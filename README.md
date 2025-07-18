# Tibia Discord Bot

A Discord bot that intelligently tracks and posts daily boosted creatures and bosses from the MMORPG Tibia. The bot automatically posts updates only when the boosted creature or boss changes, preventing spam while keeping your Discord server informed.

## Features

- 🦎 **Smart Boosted Creature Tracking**: Automatically posts when daily boosted creature changes
- 👹 **Boosted Boss Monitoring**: Tracks and announces daily boosted boss changes  
- ⏰ **Intelligent Scheduling**: Posts at 10:06 CEST (right after Tibia server boot)
- 🚫 **Anti-Spam**: Only posts when creatures/bosses actually change
- 📊 **Rich Embeds**: Beautiful Discord embeds with creature stats and information
- ⚡ **Slash Commands**: Manual update and status commands
- 🔄 **Reliable API**: Uses TibiaData API v4 for accurate data

## Quick Deploy to Railway

1. **Fork this repository** on GitHub
2. **Connect to Railway**:
   - Go to [Railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your forked repository
3. **Set Environment Variables** in Railway:
   - `DISCORD_TOKEN`: Your Discord bot token
   - `CREATURE_CHANNEL_ID`: Channel ID for boosted creature posts
   - `BOSS_CHANNEL_ID`: Channel ID for boosted boss posts
4. **Deploy** and your bot will be live!

The bot will automatically:
- Post creature updates at 10:06 CEST when they change
- Post boss updates at 10:06 CEST when they change
- Only post when there are actual changes (no spam)

## Manual Setup

### Prerequisites

- Python 3.11+
- Discord bot token ([How to create a Discord bot](https://discord.com/developers/applications))
- Two Discord channels (for creatures and bosses)
- Channel IDs from your Discord server

### Getting Discord Bot Token & Channel IDs

1. **Create Discord Bot**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" → Enter bot name → "Create"
   - Go to "Bot" tab → "Add Bot" → "Yes, do it!"
   - Copy the bot token (keep it secret!)

2. **Invite Bot to Server**:
   - Go to "OAuth2" → "URL Generator" 
   - Select "bot" scope and "Send Messages", "Use Slash Commands", "Embed Links" permissions
   - Copy the generated URL and open it to invite the bot

3. **Get Channel IDs**:
   - Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
   - Right-click on your channels → "Copy ID"
   - Save these IDs for the environment variables

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tibia-discord-bot.git
cd tibia-discord-bot
```

2. Install dependencies:
```bash
pip install -r packages.txt
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Edit `.env` file with your Discord bot token and channel IDs:
```env
DISCORD_TOKEN=your_discord_bot_token_here
CREATURE_CHANNEL_ID=123456789012345678
BOSS_CHANNEL_ID=123456789012345679
```

5. Run the bot:
```bash
python main.py
```

## Available Commands

The bot includes these slash commands:

- `/update` - Force check and post current boosted creature/boss
- `/creature` - Show detailed information about current boosted creature
- `/boss` - Show detailed information about current boosted boss
- `/next` - Show when the next server save occurs
- `/schedule` - Show the bot's automatic posting schedule

## How It Works

1. **Automatic Scheduling**: Bot checks for changes at 10:06 CEST daily (right after Tibia server boot)
2. **Change Detection**: Only posts when creatures/bosses actually change
3. **Rich Embeds**: Posts beautiful embeds with creature stats, images, and boosted benefits
4. **Backup Check**: Secondary check at 10:36 CEST if the first check fails
5. **API Integration**: Uses TibiaData API v4 for reliable, up-to-date information

## Customization

- **Custom Icon**: The bot uses a custom skull and sword icon (update the URL in `bot/embed_builder.py`)
- **Colors**: Modify embed colors in `bot/embed_builder.py`
- **Timing**: Adjust schedule in `bot/scheduler.py`
- **Channels**: Set different channels for creatures and bosses via environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
- Check the logs in Railway/your hosting platform
- Ensure your Discord bot has proper permissions
- Verify your channel IDs are correct
- Make sure the bot token is valid

## License

This project is open source and available under the MIT License.
