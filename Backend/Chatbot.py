# Import required libraries and modules
from groq import Groq
from json import load, dump
import datetime
from dotenv import load_dotenv
from os import environ

# Load environment variables from .env file
load_dotenv()

# Validate and load API keys and assistant details
GROQ_API_KEY = environ.get('GroqAPI')

if not GROQ_API_KEY:
    raise ValueError("GroqAPI key not found. Please check your .env file!")

# Initialize the Groq API client
client = Groq(api_key=GROQ_API_KEY)

# Define system message and system chat history
System = (
    f"Hello, I am {environ['NickName']}, you are a very accurate and advanced AI chatbot named {environ['AssistantName']} "
    f"which also has real-time up-to-date information from the internet.\n"
    "*** Do not tell time unless I ask, do not talk too much, just answer the question. ***\n"
    "*** Provide answers in a professional way. Make sure to use proper grammar with full stops, commas, and question marks. ***\n"
    "*** Reply in the same language as the question: Hindi in Hindi, English in English. ***\n"
    "*** Do not mention your training data or provide notes in the output. Just answer the question. ***"
)

SystemChatBot = [
    {'role': 'system', 'content': System},
    {'role': 'user', 'content': 'Hi'},
    {'role': 'assistant', 'content': 'Hello, how can I help you?'}
]

# Default message when there is no existing chat log
DefaultMessage = [
    {'role': 'user', 'content': f"Hello {environ['AssistantName']}, how are you?"},
    {'role': 'assistant', 'content': f"Welcome back {environ['NickName']}, I am doing well. How may I assist you?"}
]


def load_chat_log():
    """Loads the chat log or initializes it with default messages."""
    try:
        # Open the ChatLog.json file, and reset its contents to be empty
        with open('ChatLog.json', 'w') as f:
            dump([], f)  # Empty the file on startup
        return []  # Return an empty chat log

    except (FileNotFoundError, ValueError):  # Handles missing or corrupted JSON files
        # Create and return a new empty log
        with open('ChatLog.json', 'w') as f:
            dump([], f)
        return []


def save_chat_log(messages):
    """Saves the updated chat log to the file."""
    with open('ChatLog.json', 'w') as f:
        dump(messages, f, indent=4)


def Information():
    """
    Provides real-time information including the current day, date, and time.
    """
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime('%A')
    date = current_date_time.strftime('%d')
    month = current_date_time.strftime('%B')
    year = current_date_time.strftime('%Y')
    hour = current_date_time.strftime('%H')
    minute = current_date_time.strftime('%M')
    second = current_date_time.strftime('%S')

    data = (
        f"Use this real-time information if needed:\n"
        f"Day: {day}\n"
        f"Date: {date}\n"
        f"Month: {month}\n"
        f"Year: {year}\n"
        f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    )
    return data


def AnswerModifier(answer):
    """
    Modifies the answer by removing any empty lines.
    """
    lines = answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)


def ChatBotAI(prompt):
    """
    Handles the chatbot's logic, sending the prompt to the Groq API and updating the chat history.
    """
    messages = load_chat_log()

    try:
        # Append real-time information and user query
        input_messages = SystemChatBot + [{'role': 'system', 'content': Information()}] + messages + [
            {'role': 'user', 'content': prompt}]

        # Send request to the Groq API using the new model
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=input_messages,
            temperature=1,
            max_tokens=8192,  # max tokens supported
            top_p=1,
            stream=True,
            stop=None
        )

        # Collect the streamed response
        answer = ''
        for chunk in completion:
            answer += chunk.choices[0].delta.content or ""

        # Append the user's query and the assistant's response
        messages.append({'role': 'user', 'content': prompt})
        messages.append({'role': 'assistant', 'content': answer.strip()})

        # Save updated chat history
        save_chat_log(messages)

        # Return the modified answer
        return AnswerModifier(answer)

    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, an error occurred. Please try again later."


if __name__ == '__main__':
    print(f"{environ['AssistantName']} is ready! Type 'exit' to end the conversation.")
    while True:
        user_input = input('Enter Your Question: ')
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        print(ChatBotAI(user_input))
