
import json
import openai
import faiss
import numpy as np
import os
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class QuoteResult(BaseModel):
    text: str
    source: str

class Quote(BaseModel):
    id: int
    text: str
    source: str

# Load quotes from JSON
with open(os.path.join(os.path.dirname(__file__), 'quotes.json')) as f:
    quotes = [Quote(**q) for q in json.load(f)]
@app.get("/get_quote", response_model=List[QuoteResult])
def get_quote(user_input: str = Query(..., description="User input to match against quotes")):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set.")
    # Embed the user input
    response = openai.embeddings.create(
        input=[user_input],
        model="text-embedding-3-large"
    )
    user_vec = np.array(response['data'][0]['embedding']).astype('float32').reshape(1, -1)
    # Search FAISS for top 3
    if index.ntotal == 0:
        raise HTTPException(status_code=500, detail="FAISS index not initialized.")
    D, I = index.search(user_vec, 3)
    results = []
    for idx in I[0]:
        if idx < 0 or idx >= len(quotes):
            continue
        q = quotes[idx]
        results.append(QuoteResult(text=q.text, source=q.source))
    return results

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
