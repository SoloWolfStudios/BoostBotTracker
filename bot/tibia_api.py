import asyncio
import logging
from typing import Dict, Optional, Any
import aiohttp

logger = logging.getLogger(__name__)

class TibiaAPI:
    """Interface for TibiaData API v4"""
    
    BASE_URL = "https://api.tibiadata.com/v4"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.timeout,
                headers={
                    'User-Agent': 'TibiaDiscordBot/1.0',
                    'Accept': 'application/json'
                }
            )
        return self.session
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request to TibiaData API
        
        Args:
            endpoint: API endpoint path
            retries: Number of retry attempts
            
        Returns:
            JSON response data or None if failed
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        for attempt in range(retries + 1):
            try:
                session = await self._get_session()
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    elif response.status == 429:  # Rate limited
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"API request failed with status {response.status}: {url}")
                        
            except asyncio.TimeoutError:
                logger.error(f"Request timeout for {url} (attempt {attempt + 1})")
            except aiohttp.ClientError as e:
                logger.error(f"Client error for {url}: {e} (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Unexpected error for {url}: {e} (attempt {attempt + 1})")
            
            if attempt < retries:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
        
        logger.error(f"Failed to fetch data from {url} after {retries + 1} attempts")
        return None
    
    async def get_boosted_creatures(self) -> Optional[Dict[str, str]]:
        """
        Get current boosted creature and boss
        
        Returns:
            Dict with 'boosted_creature' and 'boosted_boss' keys, or None if failed
        """
        try:
            # Get world data to find boosted creature (using Antica as reference world)
            world_data = await self._make_request("world/Antica")
            
            boosted_creature = None
            if world_data and 'world' in world_data and 'world_information' in world_data['world']:
                world_info = world_data['world']['world_information']
                boosted_creature = world_info.get('boosted_creature')
            
            # Get boostable bosses data
            bosses_data = await self._make_request("boostablebosses")
            
            boosted_boss = None
            if bosses_data and 'boostable_bosses' in bosses_data:
                bosses_info = bosses_data['boostable_bosses']
                if 'boosted' in bosses_info and bosses_info['boosted']:
                    boosted_boss = bosses_info['boosted']['name']
            
            if boosted_creature or boosted_boss:
                result = {
                    'boosted_creature': boosted_creature,
                    'boosted_boss': boosted_boss,
                    'timestamp': world_data.get('information', {}).get('timestamp') if world_data else None
                }
                logger.info(f"Fetched boosted data: creature={boosted_creature}, boss={boosted_boss}")
                return result
            else:
                logger.warning("No boosted creature or boss found in API response")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching boosted creatures: {e}")
            return None
    
    async def get_creature_details(self, creature_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific creature
        
        Args:
            creature_name: Name of the creature
            
        Returns:
            Creature details dict or None if not found
        """
        if not creature_name:
            return None
            
        try:
            # Format creature name for API (replace spaces with underscores, lowercase)
            formatted_name = creature_name.replace(' ', '_').lower()
            
            data = await self._make_request(f"creature/{formatted_name}")
            
            if data and 'creature' in data:
                creature_info = data['creature']
                logger.info(f"Fetched details for creature: {creature_name}")
                return creature_info
            else:
                logger.warning(f"No details found for creature: {creature_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching creature details for {creature_name}: {e}")
            return None
    
    async def get_all_creatures(self) -> Optional[Dict[str, Any]]:
        """
        Get list of all creatures (for reference/debugging)
        
        Returns:
            All creatures data or None if failed
        """
        try:
            data = await self._make_request("creatures")
            
            if data and 'creatures' in data:
                logger.info("Fetched all creatures list")
                return data['creatures']
            else:
                logger.warning("Failed to fetch creatures list")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching all creatures: {e}")
            return None
    
    def format_hp(self, hp_value: Any) -> str:
        """Format HP value for display"""
        if isinstance(hp_value, (int, float)):
            return f"{int(hp_value):,}"
        elif isinstance(hp_value, str) and hp_value.isdigit():
            return f"{int(hp_value):,}"
        else:
            return str(hp_value) if hp_value else "Unknown"
    
    def format_experience(self, exp_value: Any) -> str:
        """Format experience value for display"""
        if isinstance(exp_value, (int, float)):
            return f"{int(exp_value):,}"
        elif isinstance(exp_value, str) and exp_value.isdigit():
            return f"{int(exp_value):,}"
        else:
            return str(exp_value) if exp_value else "Unknown"
    
    def get_creature_image_url(self, creature_name: str) -> str:
        """
        Get creature image URL from TibiaWiki
        
        Args:
            creature_name: Name of the creature
            
        Returns:
            Image URL string
        """
        if not creature_name:
            return ""
        
        # Format name for TibiaWiki (replace spaces with underscores)
        formatted_name = creature_name.replace(' ', '_')
        
        # TibiaWiki image URL pattern
        return f"https://tibia.fandom.com/wiki/Special:Redirect/file/{formatted_name}.gif"
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
