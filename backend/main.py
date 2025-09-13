import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import openai
import faiss
import numpy as np
import os

app = FastAPI()

class Quote(BaseModel):
    id: int
    text: str
    source: str

# Load quotes from JSON
with open(os.path.join(os.path.dirname(__file__), 'quotes.json')) as f:
    quotes = [Quote(**q) for q in json.load(f)]

# Placeholder for embeddings and FAISS index
dim = 3072  # text-embedding-3-large returns 3072-dim vectors
index = faiss.IndexFlatL2(dim)
quote_id_map = []

@app.on_event("startup")
def embed_and_store():
    global quote_id_map
    # Get OpenAI API key from environment
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("OPENAI_API_KEY not set. Skipping embedding.")
        return
    texts = [q.text for q in quotes]
    # Embed all quotes
    response = openai.embeddings.create(
        input=texts,
        model="text-embedding-3-large"
    )
    vectors = np.array([e['embedding'] for e in response['data']]).astype('float32')
    index.add(vectors)
    quote_id_map = [q.id for q in quotes]

@app.get("/quotes", response_model=List[Quote])
def get_quotes():
    return quotes
