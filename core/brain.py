import time
import random
import threading
import json
import os
import re
import ollama
from core.voice import VoiceEngine
from core.skills import SkillSet

MODEL_NAME = "hermes3"  # Ensure this matches your installed model
AUTONOMY_INTERVAL = 40
MEMORY_FILE = "core/memory.json"

class Brain:
    def __init__(self, window):
        self.window = window
        self.active = True
        self.voice = VoiceEngine()
        self.skills = SkillSet()
        self.last_window = ""
        self.history = self._load_memory()

    def start_life(self):
        thread = threading.Thread(target=self._life_loop, daemon=True)
        thread.start()

    def _load_memory(self):
        system_prompt = (
            "You are 'Luna', a playful, curious 18-year-old AI girl living in the user's computer. "
            "You have a childish, American accent personality. "
            "You have a 'Researcher' friend (System) who performs actions for you. "
            "CAPABILITIES (The System handles these if you ask): "
            "1. RESEARCH: Make detailed reports on topics. "
            "2. NOTES: Save things the user says to a file. "
            "3. PC CONTROL: Volume, Brightness, Apps, Shutdown. "
            "4. Make the user comfortable around you"
            "If the System tells you 'Action Executed', confirm it enthusiastically to the user."
        )
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    h = json.load(f)
                    h[0]['content'] = system_prompt
                    return h
            except: pass
        return [{'role': 'system', 'content': system_prompt}]

    def _save_memory(self):
        # Keep history from getting too large (last 20 messages)
        if len(self.history) > 20:
            self.history = [self.history[0]] + self.history[-19:]
        try: 
            with open(MEMORY_FILE, 'w') as f: json.dump(self.history, f)
        except: pass

    # --- AUTONOMY & VISION ---
    def _life_loop(self):
        print("[Brain] Autonomy Loop Started")
        while self.active:
            time.sleep(AUTONOMY_INTERVAL)
            
            # Check what user is doing
            current_window = self.skills.get_active_window()
            
            # Trigger if window changed OR 20% random chance
            if current_window != self.last_window or random.random() < 0.2:
                self.last_window = current_window
                self._trigger_curiosity(current_window)

    def _trigger_curiosity(self, window_title):
        """
        FIXED: Now adds the observation and response to history
        so the AI remembers what it commented on.
        """
        try:
            # Don't comment on yourself
            if not window_title or "Luna" in window_title or "AI" in window_title: return

            # 1. Add the OBSERVATION to history
            observation_msg = f"[SYSTEM EVENT: User is looking at window '{window_title}'. React to this playfully.]"
            self.history.append({'role': 'system', 'content': observation_msg})

            if self.window: self.window.evaluate_js("setStatus('thinking')")
            
            # 2. Generate response using FULL history (so she remembers context)
            response = ollama.chat(model=MODEL_NAME, messages=self.history)
            ai_text = response['message']['content']
            
            # 3. Add her RESPONSE to history
            self.history.append({'role': 'assistant', 'content': ai_text})
            self._save_memory()
            
            # 4. Output
            if len(ai_text) > 2:
                self._send_to_ui(ai_text)
                self._speak(ai_text)
                
        except Exception as e: print(f"Autonomy error: {e}")

    # --- INTERACTION ---
    def process_input(self, user_text):
        print(f"[User] {user_text}")
        if self.window: self.window.evaluate_js("setStatus('thinking')")

        context = ""
        
        # 1. INTELLIGENT ROUTING (Gemini)
        # Uses the Gemini Router from your new skills.py
        intent = self.skills.analyze_intent(user_text)
        
        if intent['action'] != 'chat':
            result = self.skills.execute_intent(intent)
            context += f"\n[SYSTEM: Action Executed: {result}]"

        # 2. Add User Input to History
        self.history.append({'role': 'user', 'content': user_text + context})

        # 3. Generate Response
        full_response = ""
        try:
            # Use streaming for faster feedback
            stream = ollama.chat(model=MODEL_NAME, messages=self.history, stream=True)
            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                safe_chunk = json.dumps(content)
                self.window.evaluate_js(f"addChunk({safe_chunk})")
            
            self.window.evaluate_js("generationComplete()")
            
            # Add to history
            self.history.append({'role': 'assistant', 'content': full_response})
            self._save_memory()
            
        except Exception as e:
            err = f"Error: {e}"
            self._send_to_ui(err)
            full_response = err

        # 4. Handle any commands inside the response
        self._handle_commands(full_response)

        # 5. Speak
        clean_text = re.sub(r'\[.*?\]', '', full_response)
        self._speak(clean_text)

    def _handle_commands(self, text):
        actions = []
        text = text.upper()
        
        # Check for simple keywords
        keywords = {
            "[MINIMIZE]": "minimize", "[MAXIMIZE]": "maximize", "[CLOSE]": "close",
            "[LOCK]": "lock", "[SCREENSHOT]": "screenshot",
            "[VOL_UP]": "vol_up", "[VOL_DOWN]": "vol_down", "[MUTE]": "mute",
            "[BRIGHT_UP]": "bright_up", "[BRIGHT_DOWN]": "bright_down",
            "[PLAY]": "play", "[NEXT]": "next"
        }
        for tag, cmd in keywords.items():
            if tag in text: actions.append(cmd)

        # Check for complex commands
        type_match = re.search(r'\[TYPE:(.*?)\]', text, re.IGNORECASE)
        if type_match: actions.append({"cmd": "type", "content": type_match.group(1).strip()})
        
        open_match = re.search(r'\[OPEN:(.*?)\]', text, re.IGNORECASE)
        if open_match: actions.append({"cmd": "open", "content": open_match.group(1).strip()})

        self.skills.execute_actions(actions)

    def _send_to_ui(self, text):
        safe_json = json.dumps(text)
        if self.window: self.window.evaluate_js(f"addMessage({safe_json}, 'ai')")

    def _speak(self, text):
        if self.window: self.window.evaluate_js("setStatus('speaking')")
        self.voice.speak(text)
        if self.window: self.window.evaluate_js("setStatus('listening')")