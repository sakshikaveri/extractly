# FastAPI listens for HTTP requests and routes them to the right function

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from extractor import extract_data

# Creating the FastAPI app
app = FastAPI(
    title="Extractly",
    description="Paste any unstructured text. Get clean structured JSON back.",
    version="1.0.0"
)


# Creating request model- what the user will be sending to us
# Pydantic automatically validates this. If 'text' is missing, FastAPI returns 422
class ExtractRequest(BaseModel):
    text: str          
    extract_type: str  # what to extract - "invoice", "email", "receipt", "custom"
    custom_fields: list[str] | None = None  # only used when extract_type is "custom", used for building own custom extraction template


# Response model 
class ExtractResponse(BaseModel):
    extract_type: str
    extracted: dict       
    confidence: str       # "high", "medium", "low" — how sure the AI is


# Health check endpoint — to confirm the server is running
@app.get("/health")
def health():
    return {"status": "ok", "service": "extractly"}


# Send JSON body - { "text": "...", "extract_type": "invoice" }
@app.post("/extract", response_model=ExtractResponse)
def extract(request: ExtractRequest):

    # Validate extract_type
    allowed_types = ["invoice", "email", "receipt", "custom"]
    if request.extract_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"extract_type must be one of: {allowed_types}"
        )

    # If type is "custom" but no custom fields provided, reject
    if request.extract_type == "custom" and not request.custom_fields:
        raise HTTPException(
            status_code=400,
            detail="When using extract_type 'custom', you must provide custom_fields list"
        )

    # Calling the extractor — this talks to OpenAI
    result = extract_data(
        text=request.text,
        extract_type=request.extract_type,
        custom_fields=request.custom_fields
    )

    return ExtractResponse(
        extract_type=request.extract_type,
        extracted=result["extracted"],
        confidence=result["confidence"]
    )