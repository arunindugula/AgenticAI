import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()

# Fallback for library integrations expecting OPENAI_API_KEY
if not os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_APIKEY"):
    os.environ["OPENAI_API_KEY"] = os.environ["OPENAI_APIKEY"]

# Load data
with open('../../data/synthetic_tickets.json', 'r') as f:
    tickets = json.load(f)

# Create documents
documents = []
for ticket in tickets:
    full_text = f"""
Ticket ID: {ticket['ticket_id']}
Title: {ticket['title']}
Description: {ticket['description']}
Resolution: {ticket['resolution']}
    """.strip()
    documents.append(Document(page_content=full_text))

print(f"Total documents: {len(documents)}")
print(f"Avg document length: {sum(len(d.page_content) for d in documents) // len(documents)} chars")
print()

# Compare chunk sizes
chunk_sizes = [100, 200, 300, 500, 1000]

print("Chunk Size | # Chunks | Avg Chunk Length")
print("-" * 45)

for size in chunk_sizes:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=size // 10
    )
    chunks = splitter.split_documents(documents)
    avg_len = sum(len(c.page_content) for c in chunks) // len(chunks) if chunks else 0
    print(f"{size:>10} | {len(chunks):>8} | {avg_len:>16}")