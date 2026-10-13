import os
from dotenv import load_dotenv
from openai import OpenAI

# Load your API key from the .env file
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY was not found. "
        "Check that your .env file exists and contains your API key."
    )

# Connect to the Groq API
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

# Select the AI model
MODEL = "openai/gpt-oss-20b"

# Store the conversation history
conversation = []

# Give your chatbot its personality and instructions
SYSTEM_INSTRUCTIONS = """
You are a friendly, intelligent AI chatbot.

Your job is to:
- Answer questions clearly and accurately.
- Explain difficult topics step by step.
- Help with coding, science, maths, and general knowledge.
- Admit when you are unsure of an answer.
- Be polite and helpful.
"""

print("=" * 45)
print("       MY PERSONAL AI CHATBOT")
print("       Powered by Groq")
print("=" * 45)
print("Type 'exit' or 'quit' to stop.")
print("Type 'clear' to clear conversation history.")
print("-" * 45)

while True:
    try:
        user_message = input("\nYou: ").strip()

        # Ignore empty messages
        if not user_message:
            continue

        # Exit the chatbot
        if user_message.lower() in ("exit", "quit"):
            print("\nBot: Goodbye! Have a great day!")
            break

        # Clear conversation history
        if user_message.lower() == "clear":
            conversation.clear()
            print("\nBot: Conversation history cleared!")
            continue

        # Add the user's message
        conversation.append({
            "role": "user",
            "content": user_message
        })

        print("\nBot: Thinking...")

        # Send the conversation to Groq
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_INSTRUCTIONS
                },
                *conversation
            ],
            temperature=0.7,
            max_tokens=1024
        )

        # Extract the response
        answer = response.choices[0].message.content

        if not answer:
            answer = "I couldn't generate a response. Please try again."

        print(f"\nBot: {answer}")

        # Save the answer for future context
        conversation.append({
            "role": "assistant",
            "content": answer
        })

    except KeyboardInterrupt:
        print("\n\nBot: Chat interrupted. Goodbye!")
        break

    except Exception as error:
        # Remove the failed user message so it can be retried
        if conversation and conversation[-1]["role"] == "user":
            conversation.pop()

        error_code = getattr(error, "code", None)
        status_code = getattr(error, "status_code", None)

        print("\nAn error occurred.")

        if status_code == 401:
            print("Your API key may be invalid.")
            print("Check GROQ_API_KEY in your .env file.")

        elif status_code == 429:
            print("You may have reached the API rate limit.")
            print("Wait a while and try again, or check your Groq usage limits.")

        elif status_code == 404:
            print("The selected model may be unavailable.")
            print("Check the model name in the Groq console.")

        else:
            print(f"Details: {error}")

        print("You can try sending your message again.")