import re
import json
import sys
from huggingface_hub import hf_hub_download

MODEL_REPO = "TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
MODEL_FILE = "mistral-7b-instruct-v0.1.Q2_K.gguf"

print("Loading AI model...")

try:
    from ctransformers import AutoModelForCausalLM as CT_Model
except ImportError:
    print("\n[ERROR] Run:  pip install ctransformers huggingface_hub")
    sys.exit(1)

model_path = hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILE)

llm = CT_Model.from_pretrained(
    model_path,
    model_type="mistral",
    context_length=4096,
    max_new_tokens=512,
    temperature=0.3,
    repetition_penalty=1.1,
    threads=4,
)

memory = {}
chat_history = []

print("\nAI Chatbot with Memory (Mistral, local)")
print("Type 'memory'  to view all stored facts.")
print("Type 'clear'   to reset conversation.")
print("Type 'exit'    to quit.\n")


def mistral_instruct(system: str, user: str, max_tokens: int = 200) -> str:
    prompt = f"<s>[INST] {system}\n\n{user} [/INST]"
    raw = llm(prompt, max_new_tokens=max_tokens)
    for stop in ["[INST]", "</s>", "[/INST]"]:
        raw = raw.split(stop)[0]
    return raw.strip()


def extract_and_update_memory(user_input: str):
    """
    Ask the LLM to extract ONLY facts explicitly stated in the message.
    Strict prompt with few-shot examples to prevent hallucination.
    """
    system = """You are a strict fact extractor. Extract ONLY personal facts that are EXPLICITLY stated in the user message. Do NOT infer, assume, or add anything not directly said.

Rules:
- Only extract what is literally written in the message.
- If nothing personal is stated, return exactly: {}
- Return ONLY a valid JSON object, nothing else.

Examples:
Message: "I like dogs" → {"likes": "dogs"}
Message: "my name is Sara" → {"name": "Sara"}
Message: "I play tennis on weekends" → {"weekend_activity": "tennis"}
Message: "I paint sometimes for fun" → {"hobby": "painting"}
Message: "my dad's name is John" → {"dad_name": "John"}
Message: "what is the weather today?" → {}
Message: "hello how are you" → {}
Message: "LLMs are trained on text data" → {}"""

    user_prompt = f'Message: "{user_input}"\nJSON:'

    raw = mistral_instruct(system, user_prompt, max_tokens=100)

    try:
        match = re.search(r'\{.*?\}', raw, re.DOTALL)
        if match:
            new_facts = json.loads(match.group())
            # Only keep string/number values, skip empty ones
            new_facts = {k: v for k, v in new_facts.items() if v and str(v).strip()}
            memory.update(new_facts)
    except Exception:
        pass


def build_chat_prompt(user_input: str) -> str:
    if memory:
        facts_str = "\n".join(f"- {k}: {v}" for k, v in memory.items())
        mem_block = (
            "Facts you know about the user (ONLY use these — never assume or add anything extra):\n"
            + facts_str
        )
    else:
        mem_block = "You don't know any personal facts about the user yet."

    system = (
        "You are a helpful, friendly AI assistant with memory. "
        "Give concise answers in 1-3 sentences unless the user asks for detail. "
        "When answering questions about the user, use ONLY the facts listed below. "
        "If a fact was not told to you, say you don't know — never guess or invent.\n\n"
        + mem_block
    )

    turns = ""
    for u, b in chat_history[-6:]:
        turns += f"[INST] {u} [/INST] {b} </s>"

    return f"<s>[INST] {system} [/INST] Understood.</s>{turns}[INST] {user_input} [/INST]"


def get_response(user_input: str) -> str:
    prompt = build_chat_prompt(user_input)
    raw = llm(prompt, max_new_tokens=200)
    for stop in ["[INST]", "</s>", "[/INST]"]:
        raw = raw.split(stop)[0]
    return raw.strip()


while True:
    try:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        if user_input.lower() == "clear":
            chat_history.clear()
            print("Bot: Conversation cleared! (Stored memory kept)\n")
            continue

        if user_input.lower() == "memory":
            if memory:
                print("\nStored Memory:")
                for k, v in memory.items():
                    print(f"  {k}: {v}")
                print()
            else:
                print("Bot: No memory stored yet.\n")
            continue

        # Step 1: extract only explicitly stated facts
        extract_and_update_memory(user_input)

        # Step 2: generate reply
        response = get_response(user_input)
        print(f"Bot: {response}\n")

        chat_history.append((user_input, response))

    except KeyboardInterrupt:
        print("\nGoodbye!")
        break
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()