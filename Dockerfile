# Use official Python image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements and install them first (for caching)
COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Expose the ports for FastAPI and Bot
EXPOSE 8000    
# FastAPI (main.py)
EXPOSE 3978    
# Teams Bot (bot.py)

# Use gunicorn for FastAPI, and run bot.py as well.
# We'll use a shell script to run both servers in parallel.

# Add an entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
