# AI Chatbot with Memory Using LangChain

A simple Python chatbot project that uses LangChain and OpenAI to maintain conversational memory across turns.

## Features

- Interactive command-line chatbot
- Conversation memory using LangChain `ConversationBufferMemory`
- Local fallback mode when API is unavailable
- Remembers user information (name, location, profession, birth date, favorites)
- Easy setup with `.env` support

## Requirements

- Python 3.10+
- OpenAI API key

## Setup

1. Create and activate a Python environment in the `chatbot` folder:

```powershell
cd chatbot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Create a `.env` file in the `chatbot` folder with:

```env
OPENAI_API_KEY=your-openai-api-key
```

## Run

```powershell
python main.py
```

## Usage

- Type a message and press Enter to chat.
- Type `history` to print the conversation history.
- Type `exit` or `quit` to stop.
- The bot remembers your personal details and answers questions about them.
