# 🧠 Balance Sheet Analyst — AI-Powered Financial Insights Assistant

**Balance Sheet Analyst** is an AI-driven interactive application that analyzes a company’s financial performance directly from its balance sheet and annual report.  
It combines structured financial data with document-level reasoning using **RAG (Retrieval-Augmented Generation)**, allowing users to ask natural-language questions like:

> “How did Reliance’s revenue change in FY 2023-24?”  
> “What are the key growth drivers mentioned in the annual report?”  
> “Compare total assets vs liabilities and comment on leverage.”

This project was developed as part of the **AI-based Financial Statement Analysis Assignment** — built end-to-end using modern open-source tools.

---
## Deployment
- ** Deployed `/backend` on [Render.com]([https://render.com](https://balance-sheet-analyst.onrender.com/docs))
- ** Deployed `/frontend/streamlit_app.py` on [Streamlit Cloud]([https://share.streamlit.io](https://balance-sheet-analyst-evezqsovn8knc8wthjnmbg.streamlit.app/)) 


## 🚀 Key Features

- **Interactive Analyst Chatbot (LLM)** — Ask any financial or qualitative question about the company.  
- **RAG-based Contextual Understanding** — Retrieves insights directly from the 100+ page annual report PDF.  
- **Dynamic Financial Dashboard** — Visualizes assets, liabilities, revenue, and profit trends using Plotly.  
- **Secure Authentication** — Role-based access (`analyst@company.com`, `ceo@company.com`).  
- **Document Parsing & Embedding Search** — Processes large PDFs into searchable knowledge chunks using FAISS.  
- **Multi-modal Context Fusion** — Combines structured JSON data + unstructured report content for richer answers.  
- **Extensible Architecture** — Modular backend (FastAPI) and frontend (Streamlit) for quick cloud deployment.

---

## 🧩 System Architecture

```
             ┌───────────────────────────┐
             │      Streamlit Frontend   │
             │  (User UI + Charts + Chat)│
             └────────────┬──────────────┘
                          │ REST API
             ┌────────────┴──────────────┐
             │       FastAPI Backend     │
             │  - Auth + Data Endpoints  │
             │  - LLM & RAG Integration  │
             └────────────┬──────────────┘
                          │
             ┌────────────┴──────────────┐
             │     RAG Engine (FAISS)    │
             │  - PDF Chunking & Embeds  │
             │  - Semantic Search Layer  │
             └────────────┬──────────────┘
                          │
             ┌────────────┴──────────────┐
             │  LLM API (Groq/OpenAI)    │
             │  - llama3 / gpt-4o-mini   │
             └───────────────────────────┘
```

---

## 🧠 Tech Stack

| Layer | Technology | Purpose |
|-------|-------------|----------|
| **Frontend** | [Streamlit](https://streamlit.io/) + Plotly | Interactive dashboard & chatbot interface |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) | REST API server with auth, data, and LLM logic |
| **LLM Engine** | [Groq API](https://groq.com/) or [OpenAI GPT] | Natural-language understanding and response |
| **RAG Engine** | [FAISS](https://github.com/facebookresearch/faiss) + [SentenceTransformers](https://www.sbert.net/) | Embedding-based similarity search for PDF |
| **Storage** | JSON / FAISS index | Financial data + vectorized document chunks |
| **Visualization** | [Plotly Express](https://plotly.com/python/plotly-express/) | Charts for assets, revenue, and profit |
| **Language** | Python 3.12 | Core development language |

---

## 🧰 Folder Structure

```
balance-sheet-analyst/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── model.py
│   │   ├── rag_utils.py
│   │   ├── settings.py
│   │   └── reliance_consolidated.pdf
│   ├── requirements.txt
│   └── ...
├── frontend/
│   └── streamlit_app.py
├── README.md
└── requirements.txt
```

---

## ⚙️ Local Setup (Step-by-Step)

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/balance-sheet-analyst.git
cd balance-sheet-analyst
```

### 2️⃣ Setup backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
```

### 3️⃣ Add your environment variables
Create a `.env` file in `backend/`:
```bash
GROQ_API_KEY=your_groq_key_here
RAG_PDF_PATH=backend/app/reliance_consolidated.pdf
RAG_MODEL=llama-3.1-8b-instant
```

### 4️⃣ Run the backend server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 5️⃣ Run the Streamlit frontend
Open a new terminal:
```bash
cd frontend
streamlit run streamlit_app.py
```

---

## 💬 Usage

1. Login with credentials: `analyst@company.com` / `analyst123`
2. View financial overview dashboard.
3. Ask financial questions in natural language.
4. Get answers powered by LLM + RAG insights.
5. Download CSV or visualize charts dynamically.

---

## ☁️ Deployment Instructions (Render + Streamlit Cloud)

**Backend (FastAPI)**  
- Deploy `/backend` folder on [Render.com](https://render.com)  
- Build Command: `pip install -r requirements.txt`  
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`  

**Frontend (Streamlit)**  
- Deploy `/frontend/streamlit_app.py` on [Streamlit Cloud](https://share.streamlit.io)  
- Set env variable: `BACKEND_URL = "https://your-backend.onrender.com"`

---

## 📈 Challenges & Learnings

- Debugged CORS errors between FastAPI and Streamlit.  
- Migrated to Groq API for faster, cheaper inference.  
- Implemented FAISS vector search for document retrieval.  
- Learned about PDF parsing, embeddings, and contextual retrieval.  
- Optimized performance with caching and normalized chat storage.

---

## 🧭 Future Enhancements

- Multi-company analysis  
- Real-time financial news integration  
- Ratio & forecasting engine  
- Persistent chat database  
- Cloud vector DB (Pinecone / Chroma) integration  

---

## 👨‍💻 Author & Credits

Developed by **[Your Name]**  
Under *Financial Data Intelligence Assignment (2025)*  
> _“Turning raw balance sheets into intelligent financial conversations — powered by AI.”_
