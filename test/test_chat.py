from test_context import save_message, load_context
import uuid

def simple_response(message: str) -> str:
    # Hardcoded response for test
    return f"I received: {message}"

if __name__ == "__main__":
    session_id = str(uuid.uuid4())
    user_id = "user_001"

    while True:
        msg = input("You: ")
        if msg.lower() in ["exit", "quit"]:
            break
        save_message(session_id, user_id, "user", msg)
        response = simple_response(msg)
        save_message(session_id, user_id, "assistant", response)
        print(f"Assistant: {response}")
        print("Context:", load_context(session_id))
