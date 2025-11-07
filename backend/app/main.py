from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import openai
from .model import load_data, USERS
from .settings import settings

app = FastAPI(title="Balance Sheet Analyst API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA = load_data(settings.DATA_PATH)


# add these imports at top of main.py
import os
from fastapi import Request
from .rag_utils import ensure_index, query_rag

# ensure index on startup (non-blocking thread)
PDF_PATH = os.getenv("RAG_PDF_PATH", "/Users/prasunndubey/Desktop/balance-sheet-analyst/backend/app/reliance_consolidated.pdf")

# optional: build index synchronously once at startup (commented if you prefer manual)
try:
    # load prebuilt RAG index (much faster)
    INDEX, META = ensure_index()
except Exception as e:
    print("RAG index ensure error:", e)
    INDEX, META = None, None
    


# ---------- Simple auth (demo only) ----------
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(req: LoginRequest):
    user = USERS.get(req.email)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "name": user.get("name", "Analyst"),
        "role": user["role"],
        "token": req.email,
        "companies": user.get("companies", ["Reliance"])  # include company list
    }

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Data endpoints ----------
@app.get("/balance-sheet")
def get_balance_sheet(token: str, company: str | None = None):
    user = USERS.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # If multi-company support exists, pick requested company if allowed
    allowed = user.get("companies", [])
    if company and (allowed != ["ALL"] and company not in allowed):
        raise HTTPException(status_code=403, detail="Not authorized for this company")

    # Demo: only one dataset is available (DATA). Return as consistent structure.
    result = {"company": DATA.get("company"), "data": DATA}
    return result
    



from fastapi import Body, HTTPException
from fastapi.responses import JSONResponse
import os, requests, json
from pydantic import BaseModel
from .rag_utils import query_rag

class AnalyzeRequest(BaseModel):
    question: str

@app.post("/analyze")
def analyze(req: AnalyzeRequest, token: str):
    """Enhanced LLM + RAG endpoint — combines balance-sheet data with retrieved PDF context."""

    # 1️⃣ Authentication
    user = USERS.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2️⃣ Structured company financial data (existing balance sheet)
    structured_context = DATA.get("figures_crore", {})

    # 3️⃣ Retrieve relevant document excerpts via RAG
    retrieved_text = ""
    try:
        retrieved_chunks = query_rag(req.question, top_k=4)
        if retrieved_chunks:
            retrieved_text = "\n\n".join(retrieved_chunks)
    except Exception as e:
        print(f"[WARN] RAG retrieval failed: {e}")

    # 4️⃣ Build final context-aware prompt
    prompt = f"""
You are a senior financial analyst AI.
Answer based on BOTH the provided structured financial data and the retrieved report excerpts.

Structured Financial Context (₹ crore):
{json.dumps(structured_context, indent=2)}

Retrieved Text from Annual Report:
{retrieved_text}

User Question:
{req.question}

Guidelines:
- Base your answer ONLY on the data above (no hallucination).
- If quantitative info is missing, say so explicitly.
- Provide short but insightful financial interpretation.
- Include relevant ratios, trends, or recommendations if applicable.
"""

    # 5️⃣ Call Groq API
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        return JSONResponse(
            content={
                "answer": "❌ Missing GROQ_API_KEY in environment. RAG retrieval shown below.",
                "retrieved": retrieved_text,
                "context": structured_context,
            },
            status_code=200,
        )

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": os.getenv("RAG_MODEL", "llama-3.1-8b-instant"),
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 600,
                "temperature": 0.3,
            },
            timeout=60,
        )
        if r.status_code != 200:
            return JSONResponse(
                content={"answer": f"LLM error: {r.status_code} {r.text}"},
                status_code=500,
            )

        answer = r.json()["choices"][0]["message"]["content"].strip()

        # ✅ Successful response
        return JSONResponse(
            content={
                "answer": answer,
                "retrieved": retrieved_text,
                "context": structured_context,
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(
            content={
                "answer": f"Unexpected error while calling Groq: {e}",
                "context": structured_context,
            },
            status_code=500,
        )
