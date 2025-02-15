from fastapi import FastAPI, HTTPException, Request
import json
from pydantic import BaseModel

app = FastAPI()

# Define a Pydantic model for documents
class Document(BaseModel):
    title: str
    metadata: dict

documents = [
    {"title": "Document 1", "metadata": {"author": "John", "year": 2020}},
    {"title": "Document 2", "metadata": {"author": "Jane", "year": 2021}},
    # Add more documents as needed
]

# New POST endpoint to create documents
@app.post("/api/documents", status_code=201)
async def create_document(document: Document):
    documents.append(document.dict())
    return document.dict()

@app.get("/api/documents/search")
async def search_documents(request: Request):
    metadata_filter = request.query_params.get("metadata")
    title_filter = request.query_params.get("title")
    filters = {}
    if metadata_filter:
        try:
            filters["metadata"] = json.loads(metadata_filter)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid metadata format")
    if title_filter:
        filters["title"] = title_filter

    results = []
    for doc in documents:
        match = True
        if "metadata" in filters:
            for key, value in filters["metadata"].items():
                if doc.get("metadata", {}).get(key) != value:
                    match = False
                    break
        if "title" in filters and filters["title"] not in doc.get("title", ""):
            match = False
        if match:
            results.append(doc)
    return results
