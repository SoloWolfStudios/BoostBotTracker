FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Python dependencies directly
RUN pip install --no-cache-dir discord.py python-dotenv aiohttp pytz apscheduler requests

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash botuser && \
    chown -R botuser:botuser /app

USER botuser

# Expose port (Railway expects this)
EXPOSE 8000

# Run the bot
CMD ["python", "main.py"]
