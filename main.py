from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import openai
import os
from dotenv import load_dotenv
from datetime import datetime
from pymongo import MongoClient

# Load environment variables
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# MongoDB setup
mongo_client = MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
db = mongo_client["poetry_db"]
poems_collection = db["poems"]

def get_response_to_prompt(prompt, model="gpt-4"):
    return client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

def save_poem(name, poem):
    # Save to MongoDB
    poem_doc = {
        "timestamp": datetime.now(),
        "name": name,
        "poem": poem
    }
    poems_collection.insert_one(poem_doc)
    
    # Also keep the file logging for backup
    with open("poems_generated.txt", "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp}\n{name}\n{poem}\n-------\n")

app = FastAPI()

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Code Poetry Generator</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
            padding: 0 20px;
        }}
        h1 {{
            font-size: 32px;
        }}
        form {{
            margin-top: 20px;
        }}
        input {{
            font-size: 24px;
            padding: 10px;
            margin: 10px;
        }}
        button {{
            font-size: 24px;
            background-color: blue;
            color: white;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
        }}
        button:hover {{
            background-color: darkblue;
        }}
        .poem {{
            font-size: 24px;
            color: purple;
            margin-top: 20px;
            white-space: pre-line;
        }}
        .poem-entry {{
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }}
        .poem-meta {{
            color: #666;
            font-size: 14px;
        }}
        .nav-links {{
            margin-top: 20px;
        }}
        .nav-links a {{
            color: blue;
            text-decoration: none;
            margin: 0 10px;
        }}
        .nav-links a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <h1>Enter Your Name to Get a Coding Poem!</h1>
    <form action="/generate" method="post">
        <input type="text" name="name" placeholder="Your name" required>
        <button type="submit">Submit</button>
    </form>
    <div class="nav-links">
        <a href="/">Home</a> | 
        <a href="/poems">View All Poems</a>
    </div>
    {poem_section}
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE.replace("{poem_section}", "")

@app.post("/generate", response_class=HTMLResponse)
async def generate_poem(name: str = Form(...)):
    prompt = f"Write a 4 line rhyming poem on {name}'s excellent coding skills. Make the poem upbeat, encouraging and humorous."
    poem = get_response_to_prompt(prompt)
    save_poem(name, poem)
    
    poem_html = f'<div class="poem">{poem}</div>'
    return HTML_TEMPLATE.replace("{poem_section}", poem_html)

# Add a new endpoint to view all poems
@app.get("/poems", response_class=HTMLResponse)
async def view_poems():
    poems = poems_collection.find().sort("timestamp", -1)
    poems_html = ""
    for poem in poems:
        timestamp = poem["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        poems_html += f"""
        <div class="poem-entry">
            <p class="poem-meta">Generated for {poem["name"]} on {timestamp}</p>
            <div class="poem">{poem["poem"]}</div>
            <hr>
        </div>
        """
    
    return HTML_TEMPLATE.replace("{poem_section}", poems_html)

# Run with: uvicorn main:app --reload
