import asyncio
import logging
from datetime import datetime, time
from typing import Optional

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

class TibiaScheduler:
    """Scheduler for Tibia bot tasks with CEST/CET timezone awareness"""
    
    def __init__(self, bot):
        self.bot = bot
        self.scheduler: Optional[AsyncIOScheduler] = None
        
        # Central European timezone (handles CET/CEST automatically)
        self.timezone = pytz.timezone('Europe/Berlin')
        
    async def start(self):
        """Start the scheduler"""
        if self.scheduler and self.scheduler.running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Initialize scheduler
            self.scheduler = AsyncIOScheduler(timezone=self.timezone)
            
            # Schedule boosted creature check at 10:06 CEST/CET daily
            # This is 4 minutes after server boot (10:02) and 6 minutes after server save (10:00)
            self.scheduler.add_job(
                func=self._check_boosted_changes,
                trigger=CronTrigger(
                    hour=10,
                    minute=6,
                    second=0,
                    timezone=self.timezone
                ),
                id='daily_boosted_check',
                name='Daily Boosted Creature/Boss Check',
                misfire_grace_time=300,  # 5 minutes grace time
                coalesce=True,  # Don't run multiple times if delayed
                max_instances=1  # Only one instance at a time
            )
            
            # Add a secondary check 30 minutes later as backup
            self.scheduler.add_job(
                func=self._backup_check,
                trigger=CronTrigger(
                    hour=10,
                    minute=36,
                    second=0,
                    timezone=self.timezone
                ),
                id='backup_boosted_check',
                name='Backup Boosted Check',
                misfire_grace_time=300,
                coalesce=True,
                max_instances=1
            )
            
            # Start the scheduler
            self.scheduler.start()
            
            logger.info("Scheduler started successfully")
            logger.info("Daily boosted check scheduled for 10:06 CEST/CET")
            logger.info("Backup check scheduled for 10:36 CEST/CET")
            
            # Log next scheduled run
            jobs = self.scheduler.get_jobs()
            for job in jobs:
                next_run = job.next_run_time
                if next_run:
                    logger.info(f"Job '{job.name}' next run: {next_run}")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    async def stop(self):
        """Stop the scheduler"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("Scheduler stopped")
    
    async def _check_boosted_changes(self):
        """Check for boosted creature/boss changes and post updates if needed"""
        try:
            logger.info("Running scheduled boosted creature/boss check")
            
            # Ensure bot is ready
            if not self.bot.is_ready():
                logger.warning("Bot not ready, skipping scheduled check")
                return
            
            # Check for changes and post updates
            result = await self.bot.post_boosted_updates(force_update=False)
            
            # Log results
            if result['creature_posted'] or result['boss_posted']:
                logger.info(f"Scheduled check completed - Creature posted: {result['creature_posted']}, Boss posted: {result['boss_posted']}")
            else:
                logger.info("Scheduled check completed - No changes detected")
            
            if result['errors']:
                for error in result['errors']:
                    logger.error(f"Scheduled check error: {error}")
            
        except Exception as e:
            logger.error(f"Error in scheduled boosted check: {e}")
    
    async def _backup_check(self):
        """Backup check in case the main check failed or missed changes"""
        try:
            logger.info("Running backup boosted creature/boss check")
            
            # Ensure bot is ready
            if not self.bot.is_ready():
                logger.warning("Bot not ready, skipping backup check")
                return
            
            # Only post if we haven't posted anything today
            current_time = datetime.now(self.timezone)
            if current_time.hour >= 10:  # Only run backup after main scheduled time
                result = await self.bot.post_boosted_updates(force_update=False)
                
                if result['creature_posted'] or result['boss_posted']:
                    logger.info(f"Backup check found changes - Creature posted: {result['creature_posted']}, Boss posted: {result['boss_posted']}")
                else:
                    logger.info("Backup check completed - No additional changes")
            
        except Exception as e:
            logger.error(f"Error in backup boosted check: {e}")
    
    def get_next_check_time(self) -> Optional[datetime]:
        """Get the next scheduled check time"""
        if not self.scheduler:
            return None
        
        job = self.scheduler.get_job('daily_boosted_check')
        if job:
            return job.next_run_time
        
        return None
    
    def get_timezone_info(self) -> str:
        """Get current timezone information"""
        now = datetime.now(self.timezone)
        tz_name = now.strftime('%Z')  # CET or CEST
        offset = now.strftime('%z')
        
        return f"{tz_name} (UTC{offset[:3]}:{offset[3:]})"
    
    async def force_check(self) -> dict:
        """Manually trigger a boosted check (for slash commands)"""
        logger.info("Manual boosted check triggered")
        return await self.bot.post_boosted_updates(force_update=True)
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self.scheduler is not None and self.scheduler.running
    
    def get_scheduler_status(self) -> dict:
        """Get detailed scheduler status"""
        if not self.scheduler:
            return {'running': False, 'jobs': 0, 'next_run': None}
        
        jobs = self.scheduler.get_jobs()
        next_run = None
        
        if jobs:
            next_runs = [job.next_run_time for job in jobs if job.next_run_time]
            if next_runs:
                next_run = min(next_runs)
        
        return {
            'running': self.scheduler.running,
            'jobs': len(jobs),
            'next_run': next_run,
            'timezone': self.get_timezone_info()
        }
