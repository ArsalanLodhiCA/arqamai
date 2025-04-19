
# generate embeddings
message_embeddings = []

for msg in messages:
    full_text = f"Subject: {msg['subject']}\n\n{msg['body']}"
    embedding = get_embedding(full_text)
    message_embeddings.append({
        "id": msg["id"],
        "embedding": embedding
    })

# 4. Save Embeddings to a New File
embeddings_path = '/content/drive/MyDrive/Al-Arqam-Project/data/message_embeddings.json'

with open(embeddings_path, 'w') as f:
    json.dump(message_embeddings, f)

