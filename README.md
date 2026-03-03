# Fantasy Quest Board

A daily-updating, D&D tavern adventurers' quest board powered by Flask + Google Gemini AI. Perfect for D&D/Drop-in sessions when a player is missing or you need quick side quests.

<img width="500" height="400" alt="image" src="https://github.com/user-attachments/assets/6c82ef16-43c5-40cb-8d08-f0beb0844896" />


## Features
- 8 fresh AI-generated quests every day (difficulty-scaled)
- Beautiful parchment notes with rotation & candlelight effects
- Fallback to hand-crafted templates if AI is down/overloaded
- Comedic grievances from the tavern crier
- Timer until quests reset
- Mobile-friendly (responsive grid)

## Prerequisites
- Python 3.9+
- Google Gemini API key (free tier works fine)

## Quick Start

1. Clone the repo
   
   git clone this repo
   cd quest-board

2. Create virtual environment
    
    python -m venv venv
    source venv/bin/activate   # Linux/macOS
    
    # or on Windows: 
    venv\Scripts\activate

3. Install dependencies
    
    pip install -r requirements.txt

4.Set your Gemini API key

   touch .env
   nano .env
   GEMINI_API_KEY=your-key-here

5.Run the app
    
    python app.py
    
open http://127.0.0.1:5000 (or your LAN IP:5000)

# Making it accessible on LAN

Python In app.py - already set:
app.run(host='0.0.0.0', port=5000, debug=True)

Use your computer's local IP (e.g. http://192.168.1.105:5000) from other devices on the same Wi-Fi.

You can adjust the port to your prefered port by changing the 
app.run port at the end of the code. 


# Running on WSGI Server

    gunicorn --workers 3 --worker-class gevent --worker-connections 1000 --bind 0.0.0.0:5000 app:app
