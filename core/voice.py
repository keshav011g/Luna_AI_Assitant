import asyncio
import edge_tts
import pygame
import os
import uuid
import time

class VoiceEngine:
    def __init__(self):
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"[Voice Init Error] {e}")
        
        # "en-US-AnaNeural" = Child/Teen American Girl
        self.voice_id = "en-US-AnaNeural" 
        self.current_file = None

    def speak(self, text):
        if not text or len(text.strip()) == 0: return
        
        # Debug log to confirm the AI is trying to speak
        print(f"[Voice] Generating audio for: {text[:30]}...")

        # Unique filename to prevent locking errors
        new_file = f"speech_{uuid.uuid4().hex}.mp3"
        try:
            # 1. Generate Audio File
            asyncio.run(self._generate_file(text, new_file))
            
            # 2. Play Audio
            self._play_audio(new_file)
            
        except Exception as e:
            print(f"[Voice Error] {e}")

    async def _generate_file(self, text, filename):
        try:
            communicate = edge_tts.Communicate(text, self.voice_id)
            await communicate.save(filename)
        except Exception as e:
            print(f"[Voice Generation Error] Is internet connected? {e}")
            raise e

    def _play_audio(self, filename):
        if not os.path.exists(filename): return

        # Stop previous playback if any
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        try: pygame.mixer.music.unload()
        except: pass

        # Clean up the previous file to save space
        if self.current_file and os.path.exists(self.current_file):
            try: os.remove(self.current_file)
            except: pass

        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            self.current_file = filename
            
            # Block to keep animation sync (with Timeout Failsafe)
            # This prevents the app from freezing forever if pygame glitches
            start_time = time.time()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                # Force stop if audio hangs for > 60 seconds
                if time.time() - start_time > 60:
                    print("[Voice] Timeout reached, stopping audio.")
                    pygame.mixer.music.stop()
                    break
            
            # Unload immediately to release file lock
            try: pygame.mixer.music.unload()
            except: pass
            
        except Exception as e:
            print(f"[Voice Playback Error] {e}")