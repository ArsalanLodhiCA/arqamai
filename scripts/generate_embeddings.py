import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables and API key
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Load messages from JSON
with open("../app/data/schoology_messages.json", "r") as f:
    messages = json.load(f)

# Function: get batched embeddings
def get_embeddings_batch(texts, model="text-embedding-3-small"):
    response = client.embeddings.create(input=texts, model=model)
    return [item.embedding for item in response.data]

# Process messages in batches
message_embeddings = []
batch_size = 100

for i in range(0, len(messages), batch_size):
    batch = messages[i:i+batch_size]
    texts = [f"Subject: {msg['subject']}\n\n{msg['body']}\n\n{msg.get('attachments_text', '')}" for msg in batch]
    embeddings = get_embeddings_batch(texts)

    for j, msg in enumerate(batch):
        message_embeddings.append({
            "id": msg["id"],
            "embedding": embeddings[j]
        })

# Save embeddings to file
embeddings_path = '../app/data/message_embeddings.json'
with open(embeddings_path, 'w') as f:
    json.dump(message_embeddings, f)
