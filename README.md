# MemoryLane

A Flask app to create and join private photo galleries by code, powered by Supabase Storage.

## Features
- Create a new gallery (generates a friendly code)
- Upload photos to `/upload?code=YOUR_CODE`
- View photos in `/gallery?code=YOUR_CODE`
- “View My Gallery” remembers your last code via session

## Setup
1. Clone the repo.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
