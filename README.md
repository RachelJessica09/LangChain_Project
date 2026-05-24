# 🤖 AI Chatbot with Memory

A fully local AI chatbot that runs on your own machine — no internet required after setup. It remembers personal facts you share during the conversation and uses them to give personalized, context-aware responses.

---

## ✨ Features

- 🧠 **AI-driven memory** — remembers your name, hobbies, family, preferences, and anything else you mention
- 🚫 **No hardcoded patterns** — the AI itself decides what's worth remembering, in any phrasing
- 🔒 **Anti-hallucination** — only stores facts you explicitly say, never invents or assumes
- 💬 **Conversation history** — maintains context across the full session
- 📴 **100% offline** — runs locally after the model is downloaded once
- ⚡ **Fast on CPU** — uses a quantized GGUF model via ctransformers

---

## 🧰 Tech Stack

| Component | Details |
|---|---|
| Model | Mistral-7B-Instruct-v0.1 (Q2_K GGUF, ~3GB) |
| Runtime | ctransformers |
| Model download | huggingface_hub |
| Language | Python 3.12 |

---

## 📁 Project Structure

```
chatbot/
├── main.py           # Main chatbot script
├── requirements.txt  # Python dependencies
├── WORKFLOW.txt      # Detailed project documentation
├── install.ps1       # PowerShell install helper
├── .gitignore        # Git ignore rules
└── README.md         # This file
```

---

## 🚀 Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install ctransformers huggingface_hub
```

### 4. Run the chatbot

```powershell
python main.py
```

> **First run** will automatically download the Mistral-7B model (~3GB). This happens once and is cached locally. Subsequent runs load from cache instantly.

---

## 💬 Usage

```
AI Chatbot with Memory (Mistral, local)
Type 'memory'  to view all stored facts.
Type 'clear'   to reset conversation.
Type 'exit'    to quit.

You: my name is Jessica
Bot: Nice to meet you, Jessica!

You: I like dogs and I play tennis on weekends
Bot: That's great! Tennis is a fun sport.

You: what is my name?
Bot: Your name is Jessica.

You: what do I do on weekends?
Bot: You play tennis on weekends.

You: what is an LLM?
Bot: A Large Language Model (LLM) is an AI trained on massive amounts of text to understand and generate human language.
```

### Commands

| Command | Action |
|---|---|
| `memory` | View all stored facts about you |
| `clear` | Reset conversation history (keeps memory) |
| `exit` / `quit` | Exit the chatbot |

---

## 🧠 How Memory Works

Every message goes through **two AI calls**:

1. **Fact Extractor** — asks the model what personal facts are in your message and stores them as JSON. Works for any phrasing — no hardcoded keywords needed.

2. **Chat Responder** — generates your reply with all stored facts injected into the system prompt, so the bot always knows who you are.

Example of what gets stored:

```
You: my dad's name is Ramana   →  {"dad_name": "Ramana"}
You: I paint sometimes for fun  →  {"hobby": "painting"}
You: I live in Chennai          →  {"location": "Chennai"}
You: what is the weather?       →  {}  (nothing personal, ignored)
```

---

## ⚙️ Model Details

**Mistral-7B-Instruct-v0.1 Q2_K**

- Developed by Mistral AI
- 7 billion parameters — outperforms larger models on most benchmarks
- Instruct-tuned for instruction following and Q&A
- Q2_K quantization reduces size from ~28GB to ~3GB with acceptable quality trade-off
- Uses Grouped Query Attention (GQA) and Sliding Window Attention (SWA) for fast CPU inference

See `WORKFLOW.txt` for full details on model selection, why other models were rejected, and how every component works.

---

## ⚠️ Known Limitations

- Memory resets on restart (not saved to disk between sessions)
- Response time is 5–15 seconds on CPU (no GPU)
- Q2_K quantization may occasionally produce slightly imperfect grammar

---

## 📄 License

MIT License — free to use, modify, and distribute.