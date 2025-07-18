#!/usr/bin/env python3
"""
Simple startup script for Railway deployment
This ensures the bot runs properly in Railway's environment
"""

import os
import sys
import subprocess

def install_dependencies():
    """Install required dependencies"""
    dependencies = [
        'discord.py>=2.5.0',
        'python-dotenv>=1.0.0', 
        'aiohttp>=3.8.0',
        'pytz>=2023.3',
        'apscheduler>=3.10.0',
        'requests>=2.31.0'
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
        except subprocess.CalledProcessError:
            print(f"Failed to install {dep}")
            continue

def main():
    """Main startup function"""
    print("Starting Tibia Discord Bot...")
    
    # Install dependencies if needed
    try:
        import discord
        import dotenv
        import aiohttp
        import pytz
        import apscheduler
        import requests
    except ImportError:
        print("Installing dependencies...")
        install_dependencies()
    
    # Import and run the main bot
    from main import main as bot_main
    import asyncio
    
    # Run the bot
    asyncio.run(bot_main())

if __name__ == "__main__":
    main()