import discord
from datetime import datetime
from typing import Dict, Any, Optional

class EmbedBuilder:
    """Builder for Discord embeds related to Tibia creatures and bosses"""
    
    # Color scheme
    CREATURE_COLOR = 0x00ff88  # Green
    BOSS_COLOR = 0xff4444     # Red
    INFO_COLOR = 0x3498db     # Blue
    ERROR_COLOR = 0xe74c3c    # Dark red
    
    def __init__(self):
        # Use the custom skull and sword icon provided by user
        self.bot_icon = "⚔️💀"
        # URL to the custom icon image (to be replaced with actual GitHub repo URL)
        self.custom_icon_url = "https://raw.githubusercontent.com/yourusername/tibia-discord-bot/main/attached_assets/ChatGPT%20Image%20Jul%2016%2C%202025%2C%2007_23_14%20PM_1752854691041.png"
        
    def create_creature_embed(self, creature_name: str, creature_details: Optional[Dict[str, Any]], boosted_data: Dict[str, Any]) -> discord.Embed:
        """
        Create embed for boosted creature announcement
        
        Args:
            creature_name: Name of the boosted creature
            creature_details: Detailed creature info from API
            boosted_data: Boosted creature data
            
        Returns:
            Discord embed object
        """
        embed = discord.Embed(
            title=f"🦎 Daily Boosted Creature",
            description=f"**{creature_name}** is today's boosted creature!",
            color=self.CREATURE_COLOR,
            timestamp=datetime.utcnow()
        )
        
        # Add creature image if available
        if creature_details and 'image_url' in creature_details:
            embed.set_thumbnail(url=creature_details['image_url'])
        else:
            # Try to construct image URL from TibiaWiki
            image_url = self._get_tibiawiki_image_url(creature_name)
            if image_url:
                embed.set_thumbnail(url=image_url)
        
        # Add basic creature stats
        if creature_details:
            self._add_creature_stats(embed, creature_details)
        else:
            embed.add_field(
                name="ℹ️ Information",
                value="Detailed creature data not available",
                inline=False
            )
        
        # Add boosted benefits
        embed.add_field(
            name="⚡ Boosted Benefits",
            value=(
                "• **2x Experience Points**\n"
                "• **2x Loot Drops**\n" 
                "• **2x Respawn Rate**"
            ),
            inline=True
        )
        
        # Add timing information
        embed.add_field(
            name="⏰ Duration",
            value="Until next server save\n(10:00 CEST daily)",
            inline=True
        )
        
        # Footer with bot branding using custom icon
        embed.set_footer(
            text=f"{self.bot_icon} TibiaBot | Data from TibiaData API",
            icon_url=self.custom_icon_url
        )
        
        return embed
    
    def create_boss_embed(self, boss_name: str, boss_details: Optional[Dict[str, Any]], boosted_data: Dict[str, Any]) -> discord.Embed:
        """
        Create embed for boosted boss announcement
        
        Args:
            boss_name: Name of the boosted boss
            boss_details: Detailed boss info from API
            boosted_data: Boosted boss data
            
        Returns:
            Discord embed object
        """
        embed = discord.Embed(
            title=f"👹 Daily Boosted Boss",
            description=f"**{boss_name}** is today's boosted boss!",
            color=self.BOSS_COLOR,
            timestamp=datetime.utcnow()
        )
        
        # Add boss image if available
        if boss_details and 'image_url' in boss_details:
            embed.set_thumbnail(url=boss_details['image_url'])
        else:
            # Try to construct image URL from TibiaWiki
            image_url = self._get_tibiawiki_image_url(boss_name)
            if image_url:
                embed.set_thumbnail(url=image_url)
        
        # Add basic boss stats
        if boss_details:
            self._add_creature_stats(embed, boss_details, is_boss=True)
        else:
            embed.add_field(
                name="ℹ️ Information", 
                value="Detailed boss data not available",
                inline=False
            )
        
        # Add boosted benefits for bosses
        embed.add_field(
            name="⚡ Boosted Benefits",
            value=(
                "• **3x Bosstiary Progress**\n"
                "• **250% Increased Loot Rate**\n"
                "• **Cooldown Reset for Everyone**"
            ),
            inline=True
        )
        
        # Add timing information
        embed.add_field(
            name="⏰ Duration",
            value="Until next server save\n(10:00 CEST daily)",
            inline=True
        )
        
        # Footer with bot branding using custom icon
        embed.set_footer(
            text=f"{self.bot_icon} TibiaBot | Data from TibiaData API",
            icon_url=self.custom_icon_url
        )
        
        return embed
    
    def _add_creature_stats(self, embed: discord.Embed, creature_details: Dict[str, Any], is_boss: bool = False) -> None:
        """
        Add creature/boss statistics to embed
        
        Args:
            embed: Discord embed to modify
            creature_details: Creature data from API
            is_boss: Whether this is a boss or regular creature
        """
        try:
            # Extract basic information
            hp = creature_details.get('hitpoints', 'Unknown')
            exp = creature_details.get('experience_points', 'Unknown')
            
            # Format HP and experience
            if isinstance(hp, (int, float)):
                hp_formatted = f"{int(hp):,}"
            else:
                hp_formatted = str(hp)
                
            if isinstance(exp, (int, float)):
                exp_formatted = f"{int(exp):,}"
            else:
                exp_formatted = str(exp)
            
            # Add stats field
            stats_value = f"❤️ **HP:** {hp_formatted}\n🌟 **Experience:** {exp_formatted}"
            
            # Add additional boss-specific info
            if is_boss:
                embed.add_field(name="📊 Boss Stats", value=stats_value, inline=True)
            else:
                embed.add_field(name="📊 Creature Stats", value=stats_value, inline=True)
            
            # Add description if available
            description = creature_details.get('description')
            if description and len(description.strip()) > 0:
                # Truncate long descriptions
                if len(description) > 200:
                    description = description[:197] + "..."
                embed.add_field(
                    name="📝 Description",
                    value=description,
                    inline=False
                )
            
            # Add loot information if available
            featured_loot = creature_details.get('loot', [])
            if featured_loot and isinstance(featured_loot, list):
                # Show first few valuable loot items
                loot_items = []
                for item in featured_loot[:3]:  # Show max 3 items
                    if isinstance(item, dict) and 'name' in item:
                        loot_items.append(item['name'])
                
                if loot_items:
                    loot_text = "\n".join([f"• {item}" for item in loot_items])
                    if len(featured_loot) > 3:
                        loot_text += f"\n• ...and {len(featured_loot) - 3} more items"
                    
                    embed.add_field(
                        name="💰 Notable Loot",
                        value=loot_text,
                        inline=True
                    )
            
        except Exception as e:
            # If there's an error parsing creature data, add a simple info field
            embed.add_field(
                name="ℹ️ Information",
                value="Unable to parse creature statistics",
                inline=False
            )
    
    def _get_tibiawiki_image_url(self, creature_name: str) -> Optional[str]:
        """
        Construct TibiaWiki image URL for creature/boss
        
        Args:
            creature_name: Name of the creature
            
        Returns:
            Image URL or None
        """
        if not creature_name:
            return None
        
        try:
            # Format name for TibiaWiki (replace spaces with underscores)
            formatted_name = creature_name.replace(' ', '_')
            
            # Return TibiaWiki image URL
            return f"https://tibia.fandom.com/wiki/Special:Redirect/file/{formatted_name}.gif"
            
        except Exception:
            return None
    
    def create_error_embed(self, title: str, description: str) -> discord.Embed:
        """
        Create error embed
        
        Args:
            title: Error title
            description: Error description
            
        Returns:
            Discord embed object
        """
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=self.ERROR_COLOR,
            timestamp=datetime.utcnow()
        )
        
        embed.set_footer(text=f"{self.bot_icon} TibiaBot", icon_url=self.custom_icon_url)
        
        return embed
    
    def create_info_embed(self, title: str, description: str) -> discord.Embed:
        """
        Create informational embed
        
        Args:
            title: Info title
            description: Info description
            
        Returns:
            Discord embed object
        """
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=self.INFO_COLOR,
            timestamp=datetime.utcnow()
        )
        
        embed.set_footer(text=f"{self.bot_icon} TibiaBot", icon_url=self.custom_icon_url)
        
        return embed
