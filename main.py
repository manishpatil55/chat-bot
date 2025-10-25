from src.chat_bot.core.chat_node import ChatNode

def main():
    bot = ChatNode()
    print("🤖 Chat-Bot (Gemini) - type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        response = bot.chat(user_input)
        print(f"Bot: {response}\n")

if __name__ == "__main__":
    main()