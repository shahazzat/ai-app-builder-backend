# ai-app-builder-backend

Below is a **ready-to-use `README.md`** for your **Colab-based Local Multi-Agent + Bolt-like UI project**.

---

```md
# Local Multi-Agent LLM Server with Bolt-like UI (Google Colab)

This project runs a **fully local, multi-agent system with multiple LLMs** inside **Google Colab**, and exposes a **Bolt-like web UI** for chatting, planning, coding, and reviewing code.

✔ No OpenAI API  
✔ Multiple local models  
✔ Multi-agent orchestration  
✔ Web UI (Monaco editor)  
✔ Runs entirely in Colab  

---

Below is a **clean, recommended project file structure** for your **Colab-based Local Multi-Agent + Bolt-like UI** project.

This structure is **scalable**, **Bolt-like**, and **easy to understand**.

---

## 📁 Project File Structure

```text
local-bolt/
├── README.md
├── .gitignore
│
├── backend/
│   ├── server.py              # FastAPI entry point
│   ├── agents.py              # Planner / Coder / Reviewer logic
│   ├── models.py              # Local LLM router (vLLM ports)
│   ├── graph.py               # LangGraph multi-agent flow
│   ├── requirements.txt
│   └── __init__.py
│
├── frontend/
│   └── bolt-ui/
│       ├── index.html
│       ├── package.json
│       ├── vite.config.js
│       ├── src/
│       │   ├── main.jsx
│       │   ├── App.jsx
│       │   ├── api.js          # Backend API calls
│       │   ├── layout/
│       │   │   ├── Sidebar.jsx     # Chat / agent panel
│       │   │   ├── Editor.jsx      # Monaco editor
│       │   │   ├── Terminal.jsx    # xterm.js console
│       │   │   └── Preview.jsx     # iframe app preview
│       │   ├── components/
│       │   │   ├── ChatBox.jsx
│       │   │   ├── Message.jsx
│       │   │   └── FileTree.jsx
│       │   ├── styles/
│       │   │   └── app.css
│       │   └── utils/
│       │       └── constants.js
│       └── public/
│           └── favicon.svg
│
├── models/
│   └── README.md               # Model download notes (optional)
│
└── notebooks/
    └── colab_setup.ipynb       # One-click Colab notebook (optional)
```

---

## 🧠 Backend Folder Explained

```text
backend/
├── server.py      → REST API (/chat)
├── models.py      → Connects to vLLM servers (ports)
├── agents.py      → Agent prompt logic
├── graph.py       → Planner → Coder → Reviewer flow
```

**Why split like this?**

* Easy to add new agents
* Easy to switch models
* Clean separation of concerns

---

## 🎨 Frontend Folder Explained (Bolt-like)

```text
frontend/bolt-ui/src/
├── layout/        → Main screen layout
├── components/    → Reusable UI pieces
├── api.js         → Backend communication
├── styles/        → Global styles
```

**Matches Bolt’s UX philosophy**:

* Sidebar → agent chat
* Center → code editor
* Bottom → terminal / preview

---

## 🧪 Minimal Version (If You Want Smaller)

```text
local-bolt/
├── server.py
├── agents.py
├── graph.py
├── requirements.txt
└── ui/
    └── src/
```

---

## 🔥 Next Recommended Additions

| Feature      | Folder               |
| ------------ | -------------------- |
| File system  | `backend/workspace/` |
| Agent memory | `backend/memory/`    |
| Docker       | `docker/`            |
| Logs         | `logs/`              |

---


## Architecture Overview

```

Browser
└── Bolt-like UI (React + Monaco)
│
▼
FastAPI Agent Server (LangGraph)
│
├── Planner LLM  (Qwen2.5-3B)
├── Coder LLM    (Qwen2.5-Coder-7B)
└── Reviewer LLM (Qwen2.5-7B)
│
▼
Local vLLM Servers (OpenAI-compatible)

````

---

## Requirements

### Google Colab
- Runtime: **GPU (T4 recommended)**
- Python ≥ 3.10
- Node ≥ 18

### Models Used
| Role | Model |
|---|---|
| Planner | `Qwen/Qwen2.5-3B-Instruct` |
| Coder | `Qwen/Qwen2.5-Coder-7B-Instruct` |
| Reviewer | `Qwen/Qwen2.5-7B-Instruct` |

---

## Installation (Colab)

### 1. System Dependencies
```bash
apt update
apt install -y nodejs npm
pip install -U pip
````

---

### 2. Python Dependencies

```bash
pip install \
  fastapi uvicorn \
  langchain langgraph langchain-openai \
  vllm pyngrok
```

---

## Running Local Models (vLLM)

⚠️ **Each command must run in a separate Colab cell and stay running.**

### Planner Model

```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-3B-Instruct \
  --port 8003
```

### Coder Model

```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --port 8001
```

### Reviewer Model

```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-7B-Instruct \
  --port 8002
```

Verify:

```bash
curl http://localhost:8001/v1/models
```

---

## Agent Server (FastAPI + LangGraph)

### `server.py`

```python
from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph

def llm(port):
    return ChatOpenAI(
        base_url=f"http://localhost:{port}/v1",
        api_key="EMPTY",
        model="local"
    )

planner = llm(8003)
coder   = llm(8001)
review  = llm(8002)

class State(dict): pass

graph = StateGraph(State)

def plan(s):
    s["plan"] = planner.invoke(s["input"]).content
    return s

def code(s):
    s["code"] = coder.invoke(s["plan"]).content
    return s

def review_code(s):
    s["review"] = review.invoke(s["code"]).content
    return s

graph.add_node("plan", plan)
graph.add_node("code", code)
graph.add_node("review", review_code)
graph.set_entry_point("plan")
graph.add_edge("plan", "code")
graph.add_edge("code", "review")

app_graph = graph.compile()

app = FastAPI()

@app.post("/chat")
def chat(prompt: str):
    return app_graph.invoke({"input": prompt})
```

Run:

```bash
uvicorn server:app --host 0.0.0.0 --port 9000
```

---

## Expose Backend (ngrok)

```python
from pyngrok import ngrok
ngrok.connect(9000)
```

Save the generated public URL.

---

## Frontend (Bolt-like UI)

### Create UI

```bash
npm create vite@latest bolt-ui -- --template react
cd bolt-ui
npm install
npm install axios @monaco-editor/react xterm
```

---

### Backend Connection (`src/api.js`)

```javascript
import axios from "axios";

export async function sendPrompt(prompt) {
  const res = await axios.post(
    "NGROK_BACKEND_URL/chat",
    null,
    { params: { prompt } }
  );
  return res.data;
}
```

Replace `NGROK_BACKEND_URL` with your ngrok backend URL.

---

### Start UI

```bash
npm run dev -- --host 0.0.0.0
```

Expose UI:

```python
ngrok.connect(5173)
```

Open the URL in your browser.

---

## Ports Summary

| Service      | Port |
| ------------ | ---- |
| Planner LLM  | 8003 |
| Coder LLM    | 8001 |
| Reviewer LLM | 8002 |
| Agent API    | 9000 |
| UI           | 5173 |

---

## Features

* Multi-agent reasoning (Planner → Coder → Reviewer)
* Multiple local models
* OpenAI-compatible local APIs
* Bolt-style coding UI
* Runs fully in Google Colab

---

## Limitations

* Colab session resets (max ~12h)
* GPU memory limited (T4)
* Not production-ready
* ngrok URLs change every session

---

## Roadmap

* File tree & workspace
* Run generated apps automatically
* Agent memory per project
* CPU-only lightweight setup
* One-click `.ipynb` notebook

---

## License

MIT License (recommended for commercial use)

---

## Credits

* vLLM
* LangChain / LangGraph
* Qwen Models
* Monaco Editor

```
