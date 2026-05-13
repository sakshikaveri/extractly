
# main.py calls this. This file does not know anything about HTTP or FastAPI, same idea as Service layer in Spring Boot.

import os
import json
import re

from dotenv import load_dotenv
from groq import Groq
from typing import Optional, List


load_dotenv()  # reads your .env file and loads the variables


# Each extract type has a predefined set of fields we want to pull out.
FIELD_MAP = {
    "invoice": [
        "vendor_name",
        "invoice_number",
        "invoice_date",
        "due_date",
        "total_amount",
        "currency",
        "line_items",
        "tax_amount",
        "payment_terms"
    ],
    "email": [
        "sender_name",
        "sender_email",
        "subject",
        "main_request_or_topic",
        "action_items",
        "urgency",
        "key_dates_mentioned"
    ],
    "receipt": [
        "store_name",
        "purchase_date",
        "items_purchased",
        "subtotal",
        "tax",
        "total",
        "payment_method"
    ]
}


def build_prompt(text: str, extract_type: str, custom_fields: Optional[List[str]]) -> str:
    if extract_type == "custom":
        fields = custom_fields
    else:
        fields = FIELD_MAP.get(extract_type)

        if not fields:
            raise ValueError(f"Unsupported extract type: {extract_type}")

    fields_str = "\n".join(f"- {field}" for field in fields)

    prompt = f"""You are a data extraction assistant.
Extract the following fields from the text below.

FIELDS TO EXTRACT:
{fields_str}

RULES:
- Return ONLY a valid JSON object. No explanation. No markdown. No extra text.
- If a field is not found in the text, set its value to null.
- For list fields (like line_items, action_items), return a proper JSON array.
- At the end, add a "confidence" field: "high" if most fields were found, "medium" if some were missing, "low" if very little was found.

TEXT TO EXTRACT FROM:
{text}

Return JSON only:"""

    return prompt


groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
def extract_data(text: str, extract_type: str, custom_fields: Optional[List[str]]) -> dict:
    # Build the prompt
    prompt = build_prompt(text, extract_type, custom_fields)

    # Call Groq
    response = groq_client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0,
    response_format={"type": "json_object"}
)

    # Get raw text
    raw_json = response.choices[0].message.content

    

    # Clean markdown fences if present
    clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_json.strip())

    # Parse JSON
    parsed = json.loads(clean)

    # Pull out confidence
    confidence = parsed.pop("confidence", "medium")

    return {
        "extracted": parsed,
        "confidence": confidence
    }