#!/bin/bash

# Start FastAPI on port 8000 in the background
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start Teams bot on port 3978 in the foreground
python bot.py
