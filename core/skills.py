import pyautogui
import psutil
import time
import os
import datetime
import webbrowser
import subprocess
import json  # <--- FIXED: Added missing import
import socket
import requests # For IP check
from plyer import notification
from google import genai
from google.genai import types
import comtypes
import shutil

# --- API KEY ---
GOOGLE_API_KEY = "Enter_Your_Gemini_API_Key_Here"

# --- OPTIONAL DEPENDENCIES ---
try: import screen_brightness_control as sbc
except ImportError: sbc = None
try: import pygetwindow as gw
except ImportError: gw = None
try: import pyperclip
except ImportError: pyperclip = None
try:
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
except ImportError: AudioUtilities = None

class SkillSet:
    def __init__(self):
        pyautogui.FAILSAFE = True 
        self.gemini_client = None
        self._init_gemini()
        
        # Ensure a workspace exists
        self.workspace = os.path.join(os.path.expanduser("~"), "Desktop", "Luna_Workspace")
        if not os.path.exists(self.workspace): os.makedirs(self.workspace)

    def _init_gemini(self):
        try:
            # Initialize client with the provided key
            self.gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
            print("[Skills] Gemini Researcher Online.")
        except Exception as e: print(f"[Skills] Gemini Error: {e}")

# --- 1. INTELLIGENT ROUTER ---
    def analyze_intent(self, user_text):
        if not self.gemini_client: return {"action": "chat"}
        
        prompt = (
            "You are a computer automation agent. You map user requests to JSON commands.\n"
            "Respond ONLY with valid JSON. Do not write explanations.\n\n"
            "Schema:\n"
            "1. REPORT: {\"action\": \"report\", \"target\": \"topic\"}\n"
            "2. NOTE: {\"action\": \"note\", \"target\": \"content\"}\n"
            "3. BROWSE: {\"action\": \"browse\", \"target\": \"url\"}\n"
            "4. OPEN APP: {\"action\": \"open\", \"target\": \"app_name\"}\n"
            "5. CLOSE APP: {\"action\": \"kill\", \"target\": \"process_name\"}\n"
            "6. FOLDER: {\"action\": \"folder\", \"target\": \"folder_name\"}\n"
            "7. SYSTEM: {\"action\": \"system\", \"target\": \"command\", \"value\": number_or_null}\n"
            "   (commands: vol_set, bright_set, mute, min, max, lock, screen, shutdown, date, ip)\n"
            "8. CHAT: {\"action\": \"chat\"}\n\n"
            f"User Request: {user_text}"
        )
        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            # --- CLEANING THE RESPONSE ---
            text = response.text.strip()
            # Remove markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                 text = text.split("```")[1].split("```")[0]
            
            return json.loads(text)
            
        except Exception as e:
            print(f"[Router Error] {e}")
            # Ensure we see the error in the terminal
            print(f"Raw Gemini Response: {response.text if 'response' in locals() else 'None'}")
            return {"action": "chat"}
    # --- 2. EXECUTION HANDLER ---
    def execute_intent(self, intent):
        action = intent.get('action')
        target = intent.get('target')
        value = intent.get('value')

        if action == "report": return self.create_report(target)
        elif action == "note": return self.take_note(target)
        elif action == "browse": webbrowser.open(target); return f"Opened {target}"
        elif action == "open": self._open_app(target); return f"Opening {target}"
        elif action == "kill": return self._kill_process(target)
        elif action == "folder": return self._create_folder(target)
        elif action == "system": return self._handle_system(target, value)
        return None

    # --- 3. MANUAL ACTIONS (For Brain.py tags) ---
    def execute_actions(self, actions):
        """Executes a list of parsed commands from Brain."""
        for action in actions:
            if isinstance(action, str):
                cmd = action.lower()
                self._handle_system(cmd, None) # Reuse system handler

            elif isinstance(action, dict):
                c = action['cmd']
                val = action.get('content', '')
                if c == "type": pyautogui.write(val, interval=0.005)
                elif c == "open": self._open_app(val)
                elif c == "browse": webbrowser.open(val)

    # --- SKILL: RESEARCH & NOTES ---
    def create_report(self, topic):
        if not self.gemini_client: return "API Key missing."
        print(f"[Skill] Researching: {topic}")
        try:
            # FIXED: Changed model to gemini-2.5-flash
            response = self.gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"Write a detailed report on: {topic}. Use Markdown.",
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            filename = f"Report_{topic.replace(' ', '_')[:20]}.md"
            filepath = os.path.join(self.workspace, filename)
            with open(filepath, "w", encoding="utf-8") as f: f.write(response.text)
            os.startfile(filepath)
            return f"Report saved: {filename}"
        except Exception as e: return f"Research failed: {e}"

    def take_note(self, text):
        try:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            filepath = os.path.join(self.workspace, f"Notes_{date_str}.txt")
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.datetime.now().strftime('%H:%M')}] {text}\n")
            return "Note saved."
        except: return "Failed to save note."

    # --- SKILL: SYSTEM CONTROL ---
    def _handle_system(self, cmd, value):
        cmd = cmd.lower()
        # Volume / Brightness
        if "vol" in cmd and "set" in cmd: self._set_volume(value); return f"Volume {value}%"
        if "bright" in cmd and "set" in cmd and sbc: sbc.set_brightness(value); return f"Brightness {value}%"
        
        # Simple Toggles
        if "mute" in cmd: pyautogui.press('volumemute')
        elif "vol" in cmd and "up" in cmd: pyautogui.press('volumeup')
        elif "vol" in cmd and "down" in cmd: pyautogui.press('volumedown')
        elif "bright" in cmd and "up" in cmd and sbc: sbc.set_brightness('+10')
        elif "bright" in cmd and "down" in cmd and sbc: sbc.set_brightness('-10')
        
        # Window / Power
        elif "min" in cmd: pyautogui.hotkey('win', 'd')
        elif "max" in cmd: pyautogui.hotkey('win', 'up')
        elif "close" in cmd: pyautogui.hotkey('alt', 'f4')
        elif "lock" in cmd: pyautogui.hotkey('win', 'l')
        elif "screen" in cmd: 
            pyautogui.screenshot(os.path.join(self.workspace, "screenshot.png"))
            return "Screenshot saved to workspace."
        elif "shutdown" in cmd: os.system("shutdown /s /t 10"); return "Shutting down in 10s!"
        
        # Media
        elif "play" in cmd or "pause" in cmd: pyautogui.press('playpause')
        elif "next" in cmd: pyautogui.press('nexttrack')
        
        # Info
        elif "date" in cmd or "time" in cmd: return datetime.datetime.now().strftime("%I:%M %p, %A, %d %B %Y")
        elif "ip" in cmd: return self._get_ip()
        
        return "Command executed."

    # --- SKILL: APP & FILES ---
    def _open_app(self, app):
        maps = {
            "chrome": "chrome", "google": "chrome", "spotify": "spotify", 
            "notepad": "notepad", "calc": "calc", "settings": "ms-settings:", 
            "explorer": "explorer", "vscode": "code", "code": "code", 
            "discord": "discord", "terminal": "cmd"
        }
        target = maps.get(app.lower(), app)
        pyautogui.press('win'); time.sleep(0.1)
        pyautogui.write(target); time.sleep(0.5)
        pyautogui.press('enter')

    def _kill_process(self, process_name):
        try:
            os.system(f"taskkill /f /im {process_name}.exe")
            return f"Killed {process_name}"
        except: return "Failed to kill process."

    def _create_folder(self, name):
        try:
            path = os.path.join(self.workspace, name)
            os.makedirs(path, exist_ok=True)
            return f"Created folder '{name}' in workspace."
        except: return "Folder creation failed."

    # --- SKILL: VOLUME & BRIGHTNESS ---
    def _set_volume(self, level):
        # 1. Validate Input
        if level is None: level = 50
        try: level = int(float(level))
        except: level = 50
        
        # Limit to safe range
        level = max(0, min(100, level))
        
        print(f"[System] Calibrating volume to {level}%...")
        pyautogui.press('volumemute') 
        pyautogui.press('volumedown', presses=50, interval=0.0)
        pyautogui.press('volumemute')
        steps_needed = int(level / 2)
        
        if steps_needed > 0:
            pyautogui.press('volumeup', presses=steps_needed, interval=0.0)
            
        return f"Volume set to {level}%"
    
    def _get_ip(self):
        try: return requests.get('https://api.ipify.org').text
        except: return "Offline"

    def get_active_window(self):
        try: return gw.getActiveWindow().title if gw else "Unknown"
        except: return "Unknown"

    def get_system_status(self):
        try:
            batt = psutil.sensors_battery().percent
            return f"Battery: {batt}%, CPU: {psutil.cpu_percent()}%"
        except: return "Unknown"
    
    def web_search(self, q): return self.ask_gemini_context(q)
    
    def ask_gemini_context(self, q):
        # Quick fallback for brain.py direct calls
        if not self.gemini_client: return "No Internet."
        try:
            # FIXED: Changed model to gemini-2.5-flash
            res = self.gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"Search Google for: {q}",
                config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
            )
            return res.text
        except: return "Search Error."
