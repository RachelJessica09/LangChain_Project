import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory


from pathlib import Path


def load_openai_api_key() -> str:
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key and "your-openai-api-key" in api_key.lower():
        api_key = None
        print("Detected placeholder API key in .env; please paste a real key.")
    while not api_key:
        api_key = input("Enter your OpenAI API key (or type 'exit' to quit): ").strip()
        if api_key.lower() == "exit":
            raise RuntimeError("OpenAI API key entry canceled by user.")
        if not api_key:
            print("No API key entered. Please paste your OpenAI API key or type 'exit'.")

    env_path = Path(__file__).resolve().parent / ".env"
    try:
        with env_path.open("w", encoding="utf-8") as env_file:
            env_file.write(f"OPENAI_API_KEY={api_key}\n")
        print(f"Saved your key to {env_path}.")
    except OSError:
        print("Could not write .env file; continuing with the entered API key.")
    os.environ["OPENAI_API_KEY"] = api_key
    return api_key


def create_chatbot() -> ConversationChain:
    api_key = load_openai_api_key()
    llm = ChatOpenAI(
        temperature=0.3,
        model_name="gpt-3.5-turbo",
        openai_api_key=api_key,
    )
    memory = ConversationBufferMemory(memory_key="history", return_messages=True)
    chain = ConversationChain(llm=llm, memory=memory, verbose=False)
    return chain


def print_history(chain: ConversationChain) -> None:
    if not hasattr(chain.memory, "chat_memory"):
        print("No conversation history available.")
        return

    messages = chain.memory.chat_memory.messages
    if not messages:
        print("No conversation history yet.")
        return

    print("\n--- Conversation history ---")
    for message in messages:
        role = message.type
        print(f"{role.capitalize()}: {message.content}")
    print("--- end history ---\n")


def main() -> None:
    try:
        chain = create_chatbot()
        using_fallback = False
    except Exception as e:
        print(f"Could not create LLM chain: {e}")
        print("Entering local fallback chat mode (no OpenAI API key).")
        chain = None
        using_fallback = True

    print("AI Chatbot with Memory using LangChain" if not using_fallback else "AI Chatbot (local fallback)")
    print("Type a message, `history` to view memory, or `exit` to quit.")

    # Local fallback chat function
    def fallback_chat(history=None, initial_prompt=None):
        if history is None:
            history = []
        user_data = {
            "name": None,
            "location": None,
            "profession": None,
            "favorite": None,
            "birth_info": None,
            "last_user_message": None,
        }

        def normalize_text(text: str) -> str:
            return text.strip().rstrip(".?")

        def extract_birth_info(text: str) -> str | None:
            lower = text.lower()
            if "i was born in" in lower:
                return normalize_text(text[lower.index("i was born in") + len("i was born in"):])
            if "i was born" in lower and "in" in lower:
                return normalize_text(text[lower.index("i was born") + len("i was born"):])
            if "my birthday is" in lower:
                return normalize_text(text[lower.index("my birthday is") + len("my birthday is"):])
            if "birthday is" in lower:
                return normalize_text(text[lower.index("birthday is") + len("birthday is"):])
            return None

        def extract_name(text: str) -> str | None:
            lower = text.lower()
            if "my name is" in lower:
                return normalize_text(text[lower.index("my name is") + len("my name is"):])
            if "i'm " in lower:
                return normalize_text(text[lower.index("i'm ") + len("i'm "):])
            if "i am " in lower:
                candidate = normalize_text(text[lower.index("i am ") + len("i am "):])
                if candidate.split()[0].lower() not in {"a", "an", "the", "from", "in", "on", "at"}:
                    return candidate
            return None

        def extract_location(text: str) -> str | None:
            lower = text.lower()
            if "live in" in lower:
                return normalize_text(text[lower.index("live in") + len("live in"):])
            if "i'm from" in lower:
                return normalize_text(text[lower.index("i'm from") + len("i'm from"):])
            if "i am from" in lower:
                return normalize_text(text[lower.index("i am from") + len("i am from"):])
            return None

        def extract_profession(text: str) -> str | None:
            lower = text.lower()
            for phrase in ["i am a", "i am an", "i'm a", "i'm an", "i work as"]:
                if phrase in lower:
                    return normalize_text(text[lower.index(phrase) + len(phrase):])
            return None

        def extract_favorite(text: str) -> str | None:
            lower = text.lower()
            if "favorite" in lower or "favourite" in lower:
                for marker in ["favorite", "favourite"]:
                    if marker in lower:
                        return normalize_text(text[lower.index(marker) + len(marker):].lstrip(" is are: "))
            if "i like" in lower:
                return normalize_text(text[lower.index("i like") + len("i like"):])
            if "i love" in lower:
                return normalize_text(text[lower.index("i love") + len("i love"):])
            return None

        def remember_fact(prompt: str) -> None:
            name = extract_name(prompt)
            if name:
                user_data["name"] = name.title()
            location = extract_location(prompt)
            if location:
                user_data["location"] = location.title()
            profession = extract_profession(prompt)
            if profession:
                user_data["profession"] = profession.title()
            favorite = extract_favorite(prompt)
            if favorite:
                user_data["favorite"] = favorite
            birth_info = extract_birth_info(prompt)
            if birth_info:
                user_data["birth_info"] = birth_info.title()
            user_data["last_user_message"] = prompt

        def build_user_data_from_history() -> None:
            for role, text in history:
                if role.lower() == "user":
                    remember_fact(text)

        def format_history() -> None:
            if not history:
                print("No conversation history yet.")
                return
            print("\n--- Conversation history ---")
            for role, text in history:
                print(f"{role}: {text}")
            print("--- end history ---\n")

        def answer_prompt(prompt: str) -> str:
            lower = prompt.lower()
            old_name = user_data["name"]
            old_location = user_data["location"]
            old_profession = user_data["profession"]
            old_favorite = user_data["favorite"]
            old_birth = user_data["birth_info"]
            remember_fact(prompt)
            if user_data["name"] and user_data["name"] != old_name:
                return f"Nice to meet you, {user_data['name']}! I'll remember that."
            if user_data["birth_info"] and user_data["birth_info"] != old_birth:
                return f"Got it! You were born in {user_data['birth_info']}."
            if user_data["location"] and user_data["location"] != old_location:
                return f"Thanks for telling me you're from {user_data['location']}!"
            if user_data["profession"] and user_data["profession"] != old_profession:
                return f"Interesting! So you work as a {user_data['profession']}."
            if user_data["favorite"] and user_data["favorite"] != old_favorite:
                return f"I'll remember that you like {user_data['favorite']}!"
            if any(q in lower for q in ["what is my name", "what's my name", "whats my name", "who am i"]):
                if user_data["name"]:
                    return f"Your name is {user_data['name']}."
                return "I don't know your name yet. Tell me by saying 'My name is ...' or 'I am ...'."
            if any(q in lower for q in ["where do i live", "where am i from", "what is my location", "where are you from", "where are i from"]):
                if user_data["location"]:
                    return f"You told me you are from {user_data['location']}."
                return "I don't know where you live yet. Tell me by saying 'I live in ...' or 'I'm from ...'."
            if any(q in lower for q in ["what do i do", "what is my profession", "what is my job", "what do i work as"]):
                if user_data["profession"]:
                    return f"You said you work as {user_data['profession']}."
                return "I don't know your profession yet. Tell me by saying 'I am a ...' or 'I work as ...'."
            if any(q in lower for q in ["what do i like", "what is my favorite", "what's my favorite", "what do i love"]):
                if user_data["favorite"]:
                    return f"You told me you like {user_data['favorite']}."
                return "I don't know your favorite things yet. Tell me by saying 'I like ...' or 'My favorite ... is ...'."
            if any(q in lower for q in ["when was i born", "when were i born", "when am i born", "when is my birthday", "what is my birthday", "when is my birthday"]):
                if user_data["birth_info"]:
                    return f"You told me you were born in {user_data['birth_info']}."
                return "I don't know your birth information yet. Tell me by saying 'I was born in ...' or 'My birthday is ...'."
            if any(q in lower for q in ["what did i say", "what did i just say", "repeat"]):
                if user_data["last_user_message"]:
                    return f"Your last message was: '{user_data['last_user_message']}'."
                return "I don't have a last message to repeat yet."
            if any(q in lower for q in ["what can you do", "what are you", "who are you", "tell me about yourself"]):
                return "I am a local fallback chatbot. I can remember what you tell me and answer simple follow-up questions based on our conversation."
            if any(q in lower for q in ["how are you", "how are you doing"]):
                return "I'm here and ready to help, even in fallback mode. Tell me more or ask a question."
            if "answer" in lower and "also" in lower:
                return "Yes, I will answer. Please ask a question or tell me something to remember."
            if any(q in lower for q in ["remember", "recall", "you told me", "what do you remember"]):
                known = []
                if user_data["name"]:
                    known.append(f"name: {user_data['name']}")
                if user_data["location"]:
                    known.append(f"location: {user_data['location']}")
                if user_data["profession"]:
                    known.append(f"profession: {user_data['profession']}")
                if user_data["favorite"]:
                    known.append(f"favorite: {user_data['favorite']}")
                if user_data["birth_info"]:
                    known.append(f"birth info: {user_data['birth_info']}")
                if known:
                    return "So far I remember: " + ", ".join(known) + "."
                return "I don't have any personal details saved yet."
            if "history" == lower:
                format_history()
                return ""
            if any(q in lower for q in ["what can i do", "how can i", "how do i", "how to"]):
                return f"That's a great question! I can help guide you through various topics. Since I'm in fallback mode, feel free to ask me anything and I'll do my best to help. {('So far I know about you: ' + ', '.join([f'{k}: {v}' for k, v in [('name', user_data['name']), ('from', user_data['location']), ('profession', user_data['profession']), ('favorite', user_data['favorite']), ('born in', user_data['birth_info'])] if v]) + '.') if any([user_data['name'], user_data['location'], user_data['profession'], user_data['favorite'], user_data['birth_info']]) else ''}"
            if any(g in lower for g in ["hello", "hi", "hey"]):
                name_part = f", {user_data['name']}" if user_data['name'] else ""
                greeting = f"Hello{name_part}! "
                greeting += "How can I help you today? Feel free to ask me anything or tell me more about yourself."
                return greeting
            if "help" in lower:
                return "I can help with many things! You can ask me questions, tell me about yourself, and I'll remember what you share. I can also discuss topics with you. What would you like to know?"
            if any(q in lower for q in ["thank", "thanks", "thankyou", "thank you"]):
                return "You're welcome! I'm happy to help. Is there anything else you'd like to know or talk about?"
            if any(q in lower for q in ["goodbye", "bye", "see you", "farewell"]):
                return "Goodbye! It was nice talking with you. Feel free to come back anytime!"
            if "?" in prompt:
                words = prompt.split()
                user_mention = ""
                if user_data["name"]:
                    user_mention = f" {user_data['name']}, I can tell you that"
                if any(q in lower for q in ["what is", "what's", "define", "explain"]):
                    word = prompt.replace("?", "").split()[-1] if prompt.split() else "that"
                    return f"That's an interesting question! {word.capitalize()} is a complex topic. I'd be happy to discuss it further if you'd like to dive deeper into it."
                if any(q in lower for q in ["why", "how come"]):
                    return f"That's a thoughtful question!{user_mention}. It's often complex, but I can share some perspective. What aspect would you like to explore?"
                if any(q in lower for q in ["do you", "can you", "have you"]):
                    return "I can try to help with that! In fallback mode, my abilities are limited compared to a full AI, but I can discuss topics, remember what you share, and provide thoughtful responses."
                return f"That's a great question!{user_mention if '?' in prompt else ''}. Tell me more about what you're curious about and I'll do my best to help."
            if any(prompt.lower().startswith(phrase) for phrase in ["tell me", "explain", "describe", "show me"]):
                return f"I'd love to help! Can you be more specific about what you'd like to know? Feel free to ask follow-up questions and I'll provide more details."
            return f"That's an interesting point! I'm here to chat and help however I can. Feel free to ask me anything else."

        build_user_data_from_history()
        if initial_prompt:
            response = answer_prompt(initial_prompt)
            if response:
                history.append(("User", initial_prompt))
                history.append(("Bot", response))
                print(f"Bot: {response}\n")

        while True:
            try:
                prompt = input("You: ").strip()
            except KeyboardInterrupt:
                print("\nGoodbye!")
                return
            
            if not prompt:
                continue
            lower = prompt.lower()
            if lower in {"exit", "quit"}:
                print("Goodbye!")
                return
            if lower == "history":
                format_history()
                continue
            history.append(("User", prompt))
            response = answer_prompt(prompt)
            if response:
                history.append(("Bot", response))
                print(f"Bot: {response}\n")

    while True:
        if using_fallback:
            fallback_chat()
            break

        try:
            prompt = input("You: ").strip()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        
        if not prompt:
            continue

        if prompt.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if prompt.lower() == "history":
            print_history(chain)
            continue

        try:
            response = chain.predict(input=prompt)
            print(f"Bot: {response}\n")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as exc:
            err = str(exc)
            print(f"Error: {err}")
            # If the error looks like an authentication/API key issue, quota issue, or rate limit, switch to fallback mode
            if any(token in err for token in [
                "Incorrect API key",
                "Authentication",
                "API key",
                "RateLimitError",
                "rate limit",
                "quota",
                "exceeded your current quota",
            ]):
                print("Detected API key/quota error — switching to local fallback chat mode.")
                using_fallback = True
                hist = None
                try:
                    if hasattr(chain, "memory") and hasattr(chain.memory, "chat_memory"):
                        msgs = chain.memory.chat_memory.messages
                        hist = [(m.type.capitalize(), m.content) for m in msgs]
                except Exception:
                    hist = None
                try:
                    fallback_chat(history=hist, initial_prompt=prompt)
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                break
            else:
                break


if __name__ == "__main__":
    main()
