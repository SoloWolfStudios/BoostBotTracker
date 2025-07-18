import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot.tibia_api import TibiaAPI
from bot.embed_builder import EmbedBuilder
from bot.scheduler import TibiaScheduler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TibiaBot(commands.Bot):
    def __init__(self):
        # Configure bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # Initialize components
        self.tibia_api = TibiaAPI()
        self.embed_builder = EmbedBuilder()
        self.scheduler = TibiaScheduler(self)
        
        # Configuration from environment
        self.creature_channel_id = int(os.getenv('CREATURE_CHANNEL_ID', '0'))
        self.boss_channel_id = int(os.getenv('BOSS_CHANNEL_ID', '0'))
        
        # Track last posted creatures/bosses to avoid duplicates
        self.last_posted_creature = None
        self.last_posted_boss = None
        
        logger.info("TibiaBot initialized")

    async def setup_hook(self):
        """Called when the bot is starting up"""
        try:
            # Sync slash commands
            await self.tree.sync()
            logger.info("Slash commands synced successfully")
            
            # Start the scheduler
            await self.scheduler.start()
            logger.info("Scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Error in setup_hook: {e}")

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="Tibia boosted creatures"
        )
        await self.change_presence(activity=activity)

    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        logger.error(f"Command error: {error}")
        await ctx.send(f"An error occurred: {str(error)}")

    async def post_boosted_updates(self, force_update: bool = False) -> dict:
        """
        Check for boosted creature/boss changes and post updates if needed
        
        Args:
            force_update: If True, posts updates regardless of change detection
            
        Returns:
            dict: Status of the update operation
        """
        result = {
            'creature_posted': False,
            'boss_posted': False,
            'errors': []
        }
        
        try:
            # Fetch current boosted data
            boosted_data = await self.tibia_api.get_boosted_creatures()
            
            if not boosted_data:
                result['errors'].append("Failed to fetch boosted data")
                return result
            
            creature_name = boosted_data.get('boosted_creature')
            boss_name = boosted_data.get('boosted_boss')
            
            # Check if creature changed or force update
            if creature_name and (force_update or creature_name != self.last_posted_creature):
                await self._post_creature_update(creature_name, boosted_data)
                self.last_posted_creature = creature_name
                result['creature_posted'] = True
                logger.info(f"Posted boosted creature update: {creature_name}")
            
            # Check if boss changed or force update
            if boss_name and (force_update or boss_name != self.last_posted_boss):
                await self._post_boss_update(boss_name, boosted_data)
                self.last_posted_boss = boss_name
                result['boss_posted'] = True
                logger.info(f"Posted boosted boss update: {boss_name}")
                
        except Exception as e:
            error_msg = f"Error posting boosted updates: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result

    async def _post_creature_update(self, creature_name: str, boosted_data: dict):
        """Post boosted creature update to configured channel"""
        if not self.creature_channel_id:
            logger.warning("Creature channel ID not configured")
            return
        
        channel = self.get_channel(self.creature_channel_id)
        if not channel:
            logger.error(f"Could not find creature channel with ID: {self.creature_channel_id}")
            return
        
        # Get detailed creature information
        creature_details = await self.tibia_api.get_creature_details(creature_name)
        
        # Build embed
        embed = self.embed_builder.create_creature_embed(creature_name, creature_details, boosted_data)
        
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            logger.error(f"No permission to send messages in creature channel: {channel.name}")
        except discord.HTTPException as e:
            logger.error(f"Failed to send creature embed: {e}")

    async def _post_boss_update(self, boss_name: str, boosted_data: dict):
        """Post boosted boss update to configured channel"""
        if not self.boss_channel_id:
            logger.warning("Boss channel ID not configured")
            return
        
        channel = self.get_channel(self.boss_channel_id)
        if not channel:
            logger.error(f"Could not find boss channel with ID: {self.boss_channel_id}")
            return
        
        # Get detailed boss information
        boss_details = await self.tibia_api.get_creature_details(boss_name)
        
        # Build embed
        embed = self.embed_builder.create_boss_embed(boss_name, boss_details, boosted_data)
        
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            logger.error(f"No permission to send messages in boss channel: {channel.name}")
        except discord.HTTPException as e:
            logger.error(f"Failed to send boss embed: {e}")

# Slash command definitions
@discord.app_commands.command(name="update", description="Force update boosted creature and boss posts")
async def update_command(interaction: discord.Interaction):
    """Slash command to manually trigger boosted updates"""
    await interaction.response.defer()
    
    try:
        bot = interaction.client
        result = await bot.post_boosted_updates(force_update=True)
        
        # Create response message
        response_parts = []
        
        if result['creature_posted']:
            response_parts.append("✅ Boosted creature updated")
        else:
            response_parts.append("⚠️ No creature update needed")
            
        if result['boss_posted']:
            response_parts.append("✅ Boosted boss updated")
        else:
            response_parts.append("⚠️ No boss update needed")
        
        if result['errors']:
            response_parts.extend([f"❌ {error}" for error in result['errors']])
        
        response = "\n".join(response_parts)
        await interaction.followup.send(response, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in update command: {e}")
        await interaction.followup.send(f"❌ Command failed: {str(e)}", ephemeral=True)

@discord.app_commands.command(name="creature", description="Check current boosted creature details")
async def creature_status_command(interaction: discord.Interaction):
    """Slash command to check current boosted creature status"""
    await interaction.response.defer()
    
    try:
        bot = interaction.client
        boosted_data = await bot.tibia_api.get_boosted_creatures()
        
        if not boosted_data:
            await interaction.followup.send("❌ Failed to fetch boosted data", ephemeral=True)
            return
        
        creature_name = boosted_data.get('boosted_creature', 'Unknown')
        
        if creature_name == 'Unknown':
            await interaction.followup.send("❌ No boosted creature found", ephemeral=True)
            return
            
        # Get detailed creature information
        creature_details = await bot.tibia_api.get_creature_details(creature_name)
        
        # Build embed
        embed = bot.embed_builder.create_creature_embed(creature_name, creature_details, boosted_data)
        embed.title = f"📊 Current Boosted Creature Status"
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in creature status command: {e}")
        await interaction.followup.send(f"❌ Command failed: {str(e)}", ephemeral=True)

@discord.app_commands.command(name="boss", description="Check current boosted boss details")
async def boss_status_command(interaction: discord.Interaction):
    """Slash command to check current boosted boss status"""
    await interaction.response.defer()
    
    try:
        bot = interaction.client
        boosted_data = await bot.tibia_api.get_boosted_creatures()
        
        if not boosted_data:
            await interaction.followup.send("❌ Failed to fetch boosted data", ephemeral=True)
            return
        
        boss_name = boosted_data.get('boosted_boss', 'Unknown')
        
        if boss_name == 'Unknown':
            await interaction.followup.send("❌ No boosted boss found", ephemeral=True)
            return
            
        # Get detailed boss information
        boss_details = await bot.tibia_api.get_creature_details(boss_name)
        
        # Build embed
        embed = bot.embed_builder.create_boss_embed(boss_name, boss_details, boosted_data)
        embed.title = f"📊 Current Boosted Boss Status"
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in boss status command: {e}")
        await interaction.followup.send(f"❌ Command failed: {str(e)}", ephemeral=True)

@discord.app_commands.command(name="next", description="Show when the next server save occurs")
async def next_save_command(interaction: discord.Interaction):
    """Slash command to show next server save time"""
    await interaction.response.defer()
    
    try:
        from datetime import datetime, timedelta
        import pytz
        
        # Central European timezone
        cet = pytz.timezone('Europe/Berlin')
        now = datetime.now(cet)
        
        # Next server save is at 10:00 CEST daily
        next_save = now.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # If it's already past 10:00 today, move to tomorrow
        if now.hour >= 10:
            next_save += timedelta(days=1)
        
        # Calculate time until next save
        time_until = next_save - now
        hours = int(time_until.total_seconds() // 3600)
        minutes = int((time_until.total_seconds() % 3600) // 60)
        
        embed = discord.Embed(
            title="⏰ Next Server Save",
            color=0x3498db,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="🕙 Next Save Time", value=f"{next_save.strftime('%H:%M %Z')}", inline=True)
        embed.add_field(name="⏳ Time Until", value=f"{hours}h {minutes}m", inline=True)
        embed.add_field(name="📅 Date", value=next_save.strftime('%Y-%m-%d'), inline=True)
        
        embed.add_field(
            name="📝 What Resets at Server Save",
            value="• Boosted Creature\n• Boosted Boss\n• Daily Rewards\n• Rashid Location\n• Boss Cooldowns",
            inline=False
        )
        
        bot = interaction.client
        embed.set_footer(text=f"{bot.embed_builder.bot_icon} TibiaBot", icon_url=bot.embed_builder.custom_icon_url)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in next save command: {e}")
        await interaction.followup.send(f"❌ Command failed: {str(e)}", ephemeral=True)

@discord.app_commands.command(name="schedule", description="Show the bot's automatic posting schedule")
async def schedule_command(interaction: discord.Interaction):
    """Slash command to show bot's posting schedule"""
    await interaction.response.defer()
    
    try:
        bot = interaction.client
        
        embed = discord.Embed(
            title="📅 Bot Schedule",
            description="When the bot automatically checks and posts updates",
            color=0x9b59b6,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🕰️ Primary Check",
            value="**10:06 CEST** daily\n(4 minutes after server boot)",
            inline=True
        )
        
        embed.add_field(
            name="🔄 Backup Check", 
            value="**10:36 CEST** daily\n(In case primary fails)",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Smart Detection",
            value="Only posts when creatures/bosses change\n(No spam!)",
            inline=False
        )
        
        # Show next scheduled check if scheduler is available
        if hasattr(bot, 'scheduler') and bot.scheduler:
            next_check = bot.scheduler.get_next_check_time()
            if next_check:
                embed.add_field(
                    name="⏰ Next Check",
                    value=f"<t:{int(next_check.timestamp())}:R>",
                    inline=False
                )
        
        embed.set_footer(text=f"{bot.embed_builder.bot_icon} TibiaBot", icon_url=bot.embed_builder.custom_icon_url)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in schedule command: {e}")
        await interaction.followup.send(f"❌ Command failed: {str(e)}", ephemeral=True)

async def main():
    """Main function to run the bot"""
    # Get bot token from environment
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set!")
        return
    
    # Validate channel configuration
    creature_channel = os.getenv('CREATURE_CHANNEL_ID')
    boss_channel = os.getenv('BOSS_CHANNEL_ID')
    
    if not creature_channel or not boss_channel:
        logger.warning("Channel IDs not configured - bot will not post updates automatically")
    
    # Create and run bot
    bot = TibiaBot()
    
    # Add slash commands to bot
    bot.tree.add_command(update_command)
    bot.tree.add_command(creature_status_command)
    bot.tree.add_command(boss_status_command)
    bot.tree.add_command(next_save_command)
    bot.tree.add_command(schedule_command)
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
