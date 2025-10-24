import os
import json
import threading
import asyncio
import base64
from time import sleep
from random import choice
import pyautogui
import mtranslate as mt
import eel
from dotenv import load_dotenv, set_key
from threading import Lock

# Import backend modules
from Backend.Extra import AnswerModifier, QueryModifier, LoadMessages, GuiMessagesConverter
from Backend.Automation import run_automation as Automation
from Backend.Automation import PROFESSIONAL_RESPONSES as professional_responses
from Backend.RSE import RealTimeChatBotAI
from Backend.Chatbot import ChatBotAI
from Backend.AutoModel import Model
from Backend.ChatGpt import ChatBotAI as ChatGptAI
from Backend.TTS import TTS

# Load environment variables
load_dotenv()

# Global variables
state = 'Available...'
messages = LoadMessages()
WEBCAM = False
js_messageslist = []
working: list[threading.Thread] = []
InputLanguage = os.environ['InputLanguage']
Assistantname = os.environ['AssistantName']
Username = os.environ['NickName']
lock = Lock()

def UniversalTranslator(Text: str) -> str:
    """Translates text to English."""
    return mt.translate(Text, 'en', 'auto').capitalize()

def MainExecution(Query: str):
    global WEBCAM, state
    print(f"[DEBUG] Entered MainExecution with query: {Query}")

    if 'en' not in InputLanguage.lower():
        Query = UniversalTranslator(Query)
    Query = QueryModifier(Query)

    if state not in ('Available...', 'Listening...', 'Processing...'):
        print("[DEBUG] Skipping execution since state is not available, listening, or processing.")
        return

    try:
        state = 'Thinking...'
        print(f"[DEBUG] State changed to: {state}")

        Decision = Model(Query)
        print(f"[DEBUG] Decision from Model: {Decision}")

        if 'general' in Decision or 'realtime' in Decision:
            if Decision[0] == 'general':
                if WEBCAM:
                    python_call_to_capture()
                    sleep(0.5)
                    Answer = ChatGptAI(Query)
                else:
                    Answer = AnswerModifier(ChatBotAI(Query))
                state = 'Answering...'
                print(f"[DEBUG] State changed to: {state}, Answer: {Answer}")
                TTS(Answer)
                eel.js_doneProcessing(Answer)  # ✅ Inform frontend
            else:
                state = 'Searching...'
                print(f"[DEBUG] State changed to: {state}")
                Answer = AnswerModifier(RealTimeChatBotAI(Query))
                state = 'Answering...'
                print(f"[DEBUG] State changed to: {state}, Answer: {Answer}")
                TTS(Answer)
                eel.js_doneProcessing(Answer)  # ✅ Inform frontend
        elif 'open webcam' in Decision:
            python_call_to_start_video()
            print('Video Started')
            WEBCAM = True
        elif 'close webcam' in Decision:
            print('Video Stopped')
            python_call_to_stop_video()
            WEBCAM = False
        else:
            state = 'Automation...'
            print(f"[DEBUG] State changed to: {state}, running automation with decision: {Decision}")
            asyncio.run(Automation(Decision,))
            response = choice(professional_responses)
            state = 'Answering...'
            print(f"[DEBUG] State changed to: {state}, response: {response}")
            with open('ChatLog.json', 'w') as f:
                json.dump(messages + [{'role': 'assistant', 'content': response}], f, indent=4)
            TTS(response)
            eel.js_doneProcessing(response)  # ✅ Inform frontend
    finally:
        state = 'Listening...'
        print(f"[DEBUG] State changed to: {state}")


@eel.expose
def js_messages():
    global messages, js_messageslist
    with lock:
        messages = LoadMessages()
    if js_messageslist != messages:
        new_messages = GuiMessagesConverter(messages[len(js_messageslist):])
        js_messageslist = messages
        return new_messages
    return []

@eel.expose
def js_state(stat=None):
    global state
    if stat:
        state = stat
    print(f"[DEBUG] Returning state to JS: {state}")
    return state

@eel.expose
def js_mic(transcription):
    global state
    print(f"[DEBUG] Received transcription: {transcription}")
    if not working or not working[0].is_alive():
        state = 'Processing...'
        print("[DEBUG] Starting MainExecution thread...")
        work = threading.Thread(target=MainExecution, args=(transcription,), daemon=True)
        work.start()
        working.clear()
        working.append(work)
    else:
        print("[DEBUG] MainExecution is already running, ignoring new input")

@eel.expose
def python_call_to_start_video():
    eel.startVideo()

@eel.expose
def python_call_to_stop_video():
    eel.stopVideo()

@eel.expose
def python_call_to_capture():
    eel.capture()

@eel.expose
def js_page(cpage=None):
    if cpage == 'home':
        eel.openHome()
    elif cpage == 'settings':
        eel.openSettings()

@eel.expose
def js_setvalues(GeminiApi, HuggingFaceApi, GroqApi, AssistantName, Username):
    print(f'GeminiApi = {GeminiApi!r} HuggingFaceApi = {HuggingFaceApi!r} GroqApi = {GroqApi!r} AssistantName = {AssistantName!r} Username = {Username!r}')
    if GeminiApi:
        set_key('.env', 'CohereAPI', GeminiApi)
    if HuggingFaceApi:
        set_key('.env', 'HuggingFaceAPI', HuggingFaceApi)
    if GroqApi:
        set_key('.env', 'GroqAPI', GroqApi)
    if AssistantName:
        set_key('.env', 'AssistantName', AssistantName)
    if Username:
        set_key('.env', 'NickName', Username)

@eel.expose
def setup():
    pyautogui.hotkey('win', 'up')

@eel.expose
def js_language():
    return InputLanguage

@eel.expose
def js_assistantname():
    return Assistantname

@eel.expose
def js_capture(image_data):
    image_bytes = base64.b64decode(image_data.split(',')[1])
    with open('capture.png', 'wb') as f:
        f.write(image_bytes)

# Initialize Eel and start the application
eel.init('web')
eel.start('spider.html', port=44444)
