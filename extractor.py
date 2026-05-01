# main.py calls this, This file does not know anything about HTTP or FastAPI, same idea as Service layer in Spring Boot.

import os
import json
from openai import OpenAI

# OpenAI client — reads the API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Each extract type has a predefined set of fields
# This way the user just says "invoice" and we know exactly what to ask for.
FIELD_MAP = {
    "invoice": [
        "vendor_name",
        "invoice_number",
        "invoice_date",
        "due_date",
        "total_amount",
        "currency",
        "line_items",      # list of items with name, quantity, price
        "tax_amount",
        "payment_terms"
    ],
    "email": [
        "sender_name",
        "sender_email",
        "subject",
        "main_request_or_topic",
        "action_items",    # list of things the sender wants to be done
        "urgency",         # high / medium / low
        "key_dates_mentioned"
    ],
    "receipt": [
        "store_name",
        "purchase_date",
        "items_purchased",  # list of items with name and price
        "subtotal",
        "tax",
        "total",
        "payment_method"
    ]
}


def build_prompt(text: str, extract_type: str, custom_fields: list[str] | None) -> str:
    """
    Build the prompt we send to OpenAI.
    The prompt tells OpenAI exactly what we want and in what format.
    """

    # Figure out which fields to extract
    if extract_type == "custom":
        fields = custom_fields
    else:
        fields = FIELD_MAP[extract_type]

    # Convert fields list to a readable string for the prompt
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


def extract_data(text: str, extract_type: str, custom_fields: list[str] | None) -> dict:
    """
    Sends the text to OpenAI and returns the structured extracted data.
    This is the core function of the whole project.
    """

    # Step 1 - Build the prompt
    prompt = build_prompt(text, extract_type, custom_fields)

    # Step 2: Call OpenAI
    # We use response_format={"type": "json_object"} to force JSON output
    # This is OpenAI's structured output mode — no more parsing markdown fences
    response = client.chat.completions.create(
        model="gpt-4o-mini",     # cheap and fast, good enough for extraction
        messages=[
            {
                "role": "system",
                "content": "You are a precise data extraction assistant. Always return valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},  # forces JSON response
        temperature=0  # 0 = deterministic, we want consistent extraction not creativity - Same input → same output
    )

    # Step 3: Parse the JSON string OpenAI returned
    raw_json = response.choices[0].message.content

    # Step 4: Convert JSON string to Python dict
    parsed = json.loads(raw_json)

    # Step 5: Pull out confidence separately, remove it from extracted data
    confidence = parsed.pop("confidence", "medium")

    return {
        "extracted": parsed,
        "confidence": confidence
    }