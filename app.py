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

# Load messages and their precomputed embeddings
with open("data/school_comm.json", "r") as f:
    messages = json.load(f)

with open("data/message_embeddings.json", "r") as f:
    message_embeddings = json.load(f)

# FastAPI app
app = FastAPI()

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

# Retreive Message - Find Original Message Text for GPT
def get_message_by_id(messages, msg_id):
    for msg in messages:
        if msg["id"] == msg_id:
            return msg
    return None


# GPT Response: Format Prompt and Ask GPT
def ask_gpt(question, context_messages):
    context_text = "\n\n".join([
        f"Subject: {msg['subject']}\n\n{msg['body']}" for msg in context_messages if msg
    ])

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





#user_question = "What time is the Quran award ceremony for 3rd grade?"
#user_question = "Which teachers put together the Quran ceremony?"

#user_question = "When is the coffee chat? is there specific time?"
#user_embedding = get_embedding(user_question)

# Step 2: Compare with Stored Message Embeddings (Cosine Similarity)





