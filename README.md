# This is Highly Experimental. It might not work on your computer

# Project Configuration Guide

This project was built with **LM Studio** and the **qwen2.5-7b-instruct** LLM in mind.
It now uses **Mem0** for long-term memory and integrates with:
- A local/remote **LLM (Large Language Model)**
- **Home Assistant** for smart home control
- **TTS (Text-to-Speech)** via GPT-SoVITS
- A custom **Spider-Bot**

---

## ⚙️ Configuration

All settings are stored in [`example.yaml`](./example.yaml).  
Copy it to `config.yaml` and update the values to match your environment:

```bash
cp example.yaml config.yaml
````

### Sections in `config.yaml`

* **LLM** → Model name, API base URL, and API key (if needed).
* **HA** → Home Assistant URL and token.
* **HA\_TOOLS** → Entity IDs (light, sensors, etc.).
* **TTS** → Text-to-Speech API endpoint and test sentence.
* **SPIDER-BOT** → Bot MAC address and network subnet.

> ⚠️ **Important:** Update the absolute path of your `config.yaml` inside `memory/memory.py`.

---

## 🔑 Generating a Home Assistant Token

1. Log in to Home Assistant.
2. Go to **Profile → Long-Lived Access Tokens**.
3. Generate a new token and copy it into `HASS_TOKEN` inside `config.yaml`.

---

## 📦 Installation (with `uv`)

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Run your project:

   ```bash
   uv run python main.py
   ```

---

## 🎙️ STT, TTS & Wake Word Options

Inside `main.py`, you can enable or disable features by setting the following flags:

```python
USE_STT = True       # Speech-to-Text
USE_TTS = True       # Text-to-Speech
USE_WAKEWORD = True  # Wake word detection
```

This gives you full control over which components are active.

---

## 🗣️ Text-to-Speech (TTS)

The project uses **GPT-SoVITS** for Text-to-Speech.
You need to **set up and start the TTS service manually** before running the project.

---

## 🙌 Credits

This project stands on the shoulders of amazing open-source tools and research:

* **[**LM Studio**](https://lmstudio.ai/)** – LLM hosting and API interface
* **[**Qwen2.5-7B-Instruct**](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)** – Language model backend
* **[**Mem0**](https://github.com/mem0ai/mem0)** – Long-term memory system
* **[**Home Assistant**](https://www.home-assistant.io/)** – Smart home integration
* **[**GPT-SoVITS**](https://github.com/RVC-Boss/GPT-SoVITS)** – Text-to-Speech engine
* **[**Vosk**](https://alphacephei.com/vosk/)** – Speech recognition / wake word detection
