from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from scipy.spatial.distance import cosine

# Loads the .env file in the current directory
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Initializes OpenAI client
client = OpenAI(api_key=api_key)

# FastAPI app
app = FastAPI()

# Initialize global variables
messages = []
message_embeddings = []

# Load files once at startup
@app.on_event("startup")
def load_files():
    global messages, message_embeddings
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    school_comm_path = os.path.join(current_dir, "data", "schoology_messages.json")
    embeddings_path = os.path.join(current_dir, "data", "message_embeddings.json")
    
    with open(school_comm_path, "r") as f:
        messages = json.load(f)
    
    with open(embeddings_path, "r") as f:
        message_embeddings = json.load(f)

# Request model
class QuestionRequest(BaseModel):
    question: str

# Embedding
def get_embedding(text, model="text-embedding-3-small"):
    response = client.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding

# Similarity
def find_most_similar(user_emb, stored_embeddings, top_k=2):
    scored = [
        (entry["id"], 1 - cosine(user_emb, entry["embedding"]))
        for entry in stored_embeddings
    ]
    top_matches = sorted(scored, key=lambda x: x[1], reverse=True)[:top_k]
    return top_matches

# Retrieve Message - Find Original Message Text for GPT
def get_message_by_id(messages, msg_id):
    for msg in messages:
        if msg["id"] == msg_id:
            return msg
    return None

# GPT Response: Format Prompt and Ask GPT
def ask_gpt(question, context_messages):
    parts = []
    for msg in context_messages:
        if not msg:
            continue
        
        entry = f"Subject: {msg.get('subject', '')}\n\nBody: {msg.get('body', '')}"
        
        # Add Attachments if available
        attachments_text = msg.get('attachments_text')
        if attachments_text:
            entry += f"\n\nAttachments: {attachments_text}"
        
        # Add Table Info if available
        table_block = msg.get('table_block')
        if table_block:
            entry += f"\n\nTable Info: {table_block}"
        
        parts.append(entry)

    # Join all entries together for context
    context_text = "\n\n---\n\n".join(parts)

    prompt = f"""
You are a helpful assistant that answers parent questions using school communications.

Context:
{context_text}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()

# POST endpoint
@app.post("/ask")
def ask_question(req: QuestionRequest):
    try:
        user_emb = get_embedding(req.question)
        top_matches = find_most_similar(user_emb, message_embeddings)
        top_contexts = [get_message_by_id(messages, match[0]) for match in top_matches]
        answer = ask_gpt(req.question, top_contexts)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
