import os
import threading
import time
import webview
from core.brain import Brain

WINDOW_WIDTH = 380
WINDOW_HEIGHT = 650

# Global brain reference to avoid circular dependency
global_brain = None

class Api:
    """Methods callable from JavaScript"""
    
    def user_message(self, text):
        """Called when user types in the HTML chatbox"""
        print(f"[UI] User input: {text}")
        if global_brain:
            threading.Thread(target=global_brain.process_input, args=(text,)).start()
        else:
            print("Brain not ready yet!")
        return {"status": "sent"}

    def frontend_ready(self):
        return {"status": "ready"}

    def resize_window(self, width, height):
        window.resize(width, height)

    def close_app(self):
        window.destroy()
        os._exit(0)

def start_background_services(window):
    """Starts AI Logic after window is visible"""
    global global_brain
    time.sleep(1.5) 
    print("[System] Starting Brain...")
    global_brain = Brain(window)
    global_brain.start_life()
    print("[System] Brain Online.")

if __name__ == '__main__':
    if not os.path.exists("assets"): os.makedirs("assets")
    if not os.path.exists("core"): os.makedirs("core")

    api = Api()

    window = webview.create_window(
        'Luna AI',
        'assets/index.html',
        js_api=api,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        transparent=True,
        on_top=True,
        frameless=True,
        draggable=True
    )

    webview.start(start_background_services, window, debug=False)