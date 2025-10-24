import os
import random
import asyncio
import platform
import subprocess
import osascript
import keyboard
import requests
from pywhatkit import search, playonyt
from webbrowser import open as webopen
from bs4 import BeautifulSoup
from PIL import Image
from os import listdir, name as os_name
from dotenv import load_dotenv
from random import randint
from rich import print
import io
import tempfile
from groq import Groq
from .import viewer_state  # Keep import since used for images (no changes there)

load_dotenv()

# Constants
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...'
PROFESSIONAL_RESPONSES = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

HUGGINGFACE_API_KEY = os.getenv('HuggingFaceAPI')
GROQ_API_KEY = os.getenv('GroqAPI')
IMAGE_DIR = '/Users/arghdas/PycharmProjects/FRIDAY/Gen_Images'

groq_client = Groq(api_key=GROQ_API_KEY)

def split_commands(command_str):
    # Replace separators with a unique delimiter
    separators = [',', ';', '\n', ' and ']
    for sep in separators:
        command_str = command_str.replace(sep, '|||')
    parts = [part.strip() for part in command_str.split('|||') if part.strip()]
    commands = []

    # Reattach arguments in parentheses or quotes
    buffer = ''
    paren_depth = 0
    quote_open = False
    for part in parts:
        paren_depth += part.count('(') - part.count(')')
        quote_open ^= part.count('"') % 2 == 1
        buffer += (' ' if buffer else '') + part
        if paren_depth == 0 and not quote_open:
            commands.append(buffer.strip())
            buffer = ''
    if buffer:
        commands.append(buffer.strip())
    return commands

def open_notepad(file):
    if os_name == 'posix':
        subprocess.Popen(['open', '-a', 'TextEdit', file])
    else:
        subprocess.Popen(['notepad.exe', file])

def content_writer_ai(prompt):
    messages = [{'role': 'user', 'content': prompt}]
    system_chat_bot = [{'role': 'system', 'content': "You're a content writer."}]
    completion = groq_client.chat.completions.create(
        model='meta-llama/llama-4-scout-17b-16e-instruct',
        messages=system_chat_bot + messages,
        max_tokens=2048,
        temperature=0.7,
        top_p=1,
        stream=True
    )

    full_text = ''
    for chunk in completion:
        delta = chunk.choices[0].delta
        if hasattr(delta, 'content') and delta.content:
            full_text += delta.content

    return full_text.replace('</s>', '')

async def content_writer_and_open(prompt):
    content = content_writer_ai(prompt)
    if not content:
        print("[red]No content generated.[/red]")
        return
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') as f:
        f.write(content)
        temp_file_path = f.name
    print(f"[green]Content saved to {temp_file_path}[/green]")
    open_notepad(temp_file_path)

async def query_image_generation(payload):
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {'Authorization': f"Bearer {HUGGINGFACE_API_KEY}"}

    try:
        response = await asyncio.to_thread(requests.post, api_url, headers=headers, json=payload)
    except requests.exceptions.RequestException as e:
        print(f"[red]Network error: {e}[/red]")
        return None

    if response.status_code != 200:
        print(f"[red]HTTP Error {response.status_code}: {response.text}[/red]")
        return None

    content_type = response.headers.get('content-type', '')
    if 'image' not in content_type:
        print(f"[red]Expected image but got: {content_type}[/red]")
        print(f"[red]Response body: {response.text[:200]}...[/red]")  # Log first 200 chars only
        return None

    return response.content


async def generate_images(prompt):
    os.makedirs(IMAGE_DIR, exist_ok=True)
    tasks = [
        asyncio.create_task(query_image_generation({
            'inputs': f'{prompt}, 4K resolution, hyper-realistic, ultra detailed, seed={randint(0, 1000000)}'
        })) for _ in range(2)
    ]
    image_bytes_list = await asyncio.gather(*tasks)

    filenames = []
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes is None:
            print(f"[red]Skipping image {i + 1}: Invalid data[/red]")
            continue
        file_path = os.path.join(IMAGE_DIR, f'image{i + 1}.jpg')
        with open(file_path, 'wb') as f:
            f.write(image_bytes)
        filenames.append(file_path)

    if not filenames:
        print("[red]No valid images generated.[/red]")
        return None

    viewer = ShowImage(filenames)
    viewer.show_current_image()
    return viewer

class ShowImage:
    def __init__(self, image_paths):
        self.image_paths = image_paths
        self.index = 0

    def show_current_image(self):
        try:
            image_path = self.image_paths[self.index]
            if platform.system() == "Darwin":
                subprocess.run(["open", image_path])
            elif platform.system() == "Windows":
                os.startfile(image_path)
            elif platform.system() == "Linux":
                subprocess.run(["xdg-open", image_path])
            else:
                print(f"[red]Unsupported platform to open image: {platform.system()}[/red]")
        except Exception as e:
            print(f"[red]Error opening image: {e}[/red]")

    def next_image(self):
        self.index = (self.index + 1) % len(self.image_paths)
        self.show_current_image()

    def previous_image(self):
        self.index = (self.index - 1) % len(self.image_paths)
        self.show_current_image()

    def close_image(self):
        print("[yellow]Please manually close image windows.[/yellow]")

def delete_images():
    if not os.path.exists(IMAGE_DIR):
        return
    for file in os.listdir(IMAGE_DIR):
        file_path = os.path.join(IMAGE_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    print("[green]All images deleted from Gen_Images.[/green]")

def system_command(command):
    command = command.strip().lower().strip('()"\'')

    commands = {
        'mute': lambda: osascript.run('set volume output muted true'),
        'unmute': lambda: osascript.run('set volume output muted false'),
        'volume up': lambda: osascript.run('set volume output volume (output volume of (get volume settings) + 10)'),
        'volume down': lambda: osascript.run('set volume output volume (output volume of (get volume settings) - 10)'),
        'minimize all': lambda: subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "h" using {command down}']),
    }

    if command in commands:
        try:
            result = commands[command]()
            print(f"[green]System command executed: {command}[/green]")
            return True
        except Exception as e:
            print(f"[red]Failed to execute system command '{command}': {e}[/red]")
            return False

    print(f"[yellow]Unknown system command: {command}[/yellow]")
    return False

def open_app(app_name):
    try:
        apps = {
            "notepad": "TextEdit",
            "calculator": "Calculator",
            "paint": "Preview"
        }
        subprocess.run(['open', '-a', apps.get(app_name.lower(), app_name)])
        return True
    except Exception:
        return False

def close_app(app_name):
    try:
        subprocess.run(['osascript', '-e', f'tell application "{app_name}" to quit'])
        return True
    except Exception:
        return False

def play_youtube(query):
    url = playonyt(query, open_video=False)  # Get video URL only
    if url and "watch?v=" in url:
        url += "&autoplay=1"
        osascript.run(f'tell application "Safari" to open location \"{url}\"')
    return True



async def execute_commands(commands, client=None):
    responses = []

    for command in commands:
        command = command.lower().strip()

        if command.startswith('open '):
            app = command.removeprefix('open ')
            success = open_app(app)
            responses.append(f"{'Opened' if success else 'Failed to open'} {app}.")

        elif command.startswith('close '):
            app = command.removeprefix('close ')
            success = close_app(app)
            responses.append(f"{'Closed' if success else 'Failed to close'} {app}.")

        elif command.startswith('play '):
            success = play_youtube(command.removeprefix('play '))
            responses.append("Done sir. Playing on YouTube." if success else "Failed to play video.")

        elif command.startswith('system '):
            success = system_command(command.removeprefix('system '))
            responses.append("System command executed." if success else "System command failed.")

        elif command.startswith('generate image'):
            start_paren = command.find('(')
            end_paren = command.find(')')
            start_quote = command.find('"')
            end_quote = command.rfind('"')
            if start_paren != -1 and end_paren != -1 and start_paren < end_paren:
                prompt = command[start_paren + 1:end_paren].strip()
            elif start_quote != -1 and end_quote != -1 and start_quote < end_quote:
                prompt = command[start_quote + 1:end_quote].strip()
            else:
                prompt = command.replace("generate image", "").strip()
            viewer_state.image_viewer = await generate_images(prompt)
            responses.append("Images generated.")

        elif command in ('next image', 'change image'):
            if viewer_state.image_viewer:
                viewer_state.image_viewer.next_image()
                responses.append("Next image displayed.")
            else:
                responses.append("No image viewer initialized.")

        elif command == 'previous image':
            if viewer_state.image_viewer:
                viewer_state.image_viewer.previous_image()
                responses.append("Previous image displayed.")
            else:
                responses.append("No image viewer initialized.")

        elif command == 'close image':
            if viewer_state.image_viewer:
                viewer_state.image_viewer.close_image()
                viewer_state.image_viewer = None
                responses.append("Image viewer closed.")
            else:
                responses.append("No image to close.")

        elif command == 'delete images':
            delete_images()
            responses.append("All images deleted.")

        elif command.startswith('google search '):
            search(command.removeprefix('google search '))
            responses.append("Google search performed.")

        elif command.startswith('youtube search '):
            playonyt(command.removeprefix('youtube search '))
            responses.append("Searched on YouTube.")

        elif command.startswith('content '):
            prompt = command[len('content '):].strip()
            await content_writer_and_open(prompt)
            responses.append("Content generated and opened in Notepad.")

        elif command == 'general':
            responses.append("General intent received.")

        else:
            responses.append(f"No match for: {command}")

    return responses


async def run_automation(commands, client=None):
    if isinstance(commands, str):
        commands = split_commands(commands)
    responses = await execute_commands(commands, client)

    if responses:
        return " ".join(responses)
    else:
        return random.choice(PROFESSIONAL_RESPONSES)
