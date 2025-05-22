# AI Poem Generator

A web application that generates personalized poems using OpenAI's GPT-4o model.

## Features

- Creates a custom 4-line poem based on user's name
- Stores poems in MongoDB for persistent history
- Simple, responsive web interface
- Built with FastAPI and Python

## Setup

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
4. Install dependencies: `pip install fastapi uvicorn openai python-dotenv pymongo`
5. Create a `.env` file with your API keys: