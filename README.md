<h1 align="center">Luna AI Desktop Assistant</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/UI-PyWebView-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/LLM-Ollama-black?style=for-the-badge&logo=ollama" />
  <img src="https://img.shields.io/badge/Voice-Edge--TTS-green?style=for-the-badge" />
</p>

<p align="center">
  <strong>An autonomous, voice-activated desktop companion that lives on your PC.</strong>
</p>

<p align="center">
  <!-- REPLACE THIS PATH WITH A SCREENSHOT OF YOUR APP IF YOU HAVE ONE -->
  <!-- <img src="assets/screenshot_demo.png" alt="Luna AI UI" width="600"> -->
</p>

## 📖 About
Luna is a local AI assistant designed to bridge the gap between chatbots and operating system control. Unlike standard web AIs, Luna lives natively on your desktop. She combines the conversational capabilities of **Ollama (Hermes 3)** with the research power of **Google Gemini** and the system automation of **Python**.

She features a transparent, overlay-style UI inspired by sci-fi aesthetics, providing real-time voice feedback and system control.

## ✨ Key Features

### 🧠 Intelligent Core
* **Local LLM:** Powered by Ollama (default: `hermes3`) for low-latency, private chatting.
* **Personality:** Distinct "Luna" persona—playful, curious, and interactive.
* **Context Memory:** Remembers conversation history (stored locally in `memory.json`).

### 🛠 System Automation
* **Volume Control:** Adjusts system volume via keyboard simulation (ensures compatibility with all Windows drivers).
* **App Management:** Open and close applications (Spotify, Chrome, VS Code, etc.) by name.
* **PC Controls:** Lock screen, take screenshots, shutdown, and control brightness.

### 🌐 Research & Tools
* **Internet Access:** Uses Google Gemini API to perform live web searches.
* **Report Generation:** Can write detailed markdown reports on any topic and save them to your workspace.
* **Note Taking:** Dictate notes that are automatically time-stamped and saved to text files.

### 🗣️ Voice Interaction
* **Text-to-Speech:** High-quality, emotive voice using Microsoft Edge TTS (No API costs).
* **Visual Feedback:** "Arc Reactor" UI animation that reacts to listening, thinking, and speaking states.

## ⚙️ Tech Stack
* **Frontend:** HTML5, CSS3, JavaScript (Transparent Overlay).
* **Backend:** Python.
* **UI Framework:** `pywebview`.
* **AI Backend:** `ollama` (Local) & `google-genai` (Cloud).
* **Automation:** `pyautogui`, `psutil`.

## 🚀 Installation

### Prerequisites
1.  **Python 3.10+** installed.
2.  **[Ollama](https://ollama.com/)** installed and running.
3.  A **Google Gemini API Key** (Free tier available).

### Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/Luna_AI_Assistant.git](https://github.com/YOUR_USERNAME/Luna_AI_Assistant.git)
    cd Luna_AI_Assistant
    ```

2.  **Install Python Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Download the LLM Model**
    Open your terminal and pull the model Luna uses (default is `hermes3`, but you can change this in `brain.py`):
    ```bash
    ollama pull hermes3
    ```

4.  **Configure API Keys**
    * Open `core/skills.py`.
    * Find the line `GOOGLE_API_KEY = "..."`.
    * Replace it with your actual Gemini API Key.
    * *(Recommended: Use a .env file for security in production).*

## 🎮 Usage

1.  Make sure Ollama is running in the background.
2.  Run the main script:
    ```bash
    python main.py
    ```
3.  **Commands to try:**
    * *"Turn volume to 50."*
    * *"Open Spotify."*
    * *"Make a report on Quantum Mechanics."*
    * *"Take a note: Buy milk."*
    * *"Lock the screen."*
## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the project.
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the Branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
<p align="center">
  Made with ❤️ by keshav011g
</p>
