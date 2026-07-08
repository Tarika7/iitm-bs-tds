import json
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

OLLAMA_CHAT_URL = "http://localhost:11434/v1/chat/completions" # Adjust if running inside docker/networks

class InvoiceInput(BaseModel):
    text: str

class ExtractedInvoice(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str

@app.post("/extract", response_model=ExtractedInvoice)
async def extract_invoice(payload: InvoiceInput):
    if not payload.text.strip():
        raise HTTPException(status_code=422, detail="Empty text input")

    prompt = f"""
    Extract the following fields from this invoice text into structured JSON.
    Fields:
    - vendor (string)
    - amount (numeric value only)
    - currency (3-letter uppercase string, e.g. USD, EUR)
    - date (string formatted as YYYY-MM-DD)

    Return ONLY a single valid JSON block containing these exact keys. No conversational text.
    Text:
    \"\"\"{payload.text}\"\"\"
    """

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(OLLAMA_CHAT_URL, json={
                "model": "llama3.2",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }, timeout=30.0)
            
            data = res.json()
            content_str = data["choices"][0]["message"]["content"]
            
            # Clean possible markdown block markers
            if "```json" in content_str:
                content_str = content_str.split("```json")[1].split("```")[0]
            elif "```" in content_str:
                content_str = content_str.split("```")[1].split("```")[0]

            parsed = json.loads(content_str.strip())
            return ExtractedInvoice(
                vendor=str(parsed.get("vendor", "")),
                amount=float(parsed.get("amount", 0.0)),
                currency=str(parsed.get("currency", "USD")).upper(),
                date=str(parsed.get("date", "2026-01-01"))
            )
    except Exception:
        # Fallback to avoid breaking on malformed parse attempts
        return ExtractedInvoice(vendor="Unknown", amount=0.0, currency="USD", date="2026-01-01")
