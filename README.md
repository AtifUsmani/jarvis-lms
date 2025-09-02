
# Project Configuration Guide

This project uses **`uv`** as the package manager and includes integrations with:
- A local/remote **LLM (Large Language Model)**
- **MongoDB** for database storage
- **Home Assistant** for smart home control
- **TTS (Text-to-Speech)** service
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
* **DB** → MongoDB connection string.
* **HA** → Home Assistant URL and token.
* **HA\_TOOLS** → Entity IDs (light, sensors, etc.).
* **TTS** → Text-to-Speech API endpoint and test sentence.
* **SPIDER-BOT** → Bot MAC address and network subnet.

---

## 🔑 Generating a Home Assistant Token

1. Log in to Home Assistant.
2. Go to **Profile → Long-Lived Access Tokens**.
3. Generate a new token and copy it into `HASS_TOKEN` inside `config.yaml`.

---

## 🗄️ Database Setup

Install MongoDB locally or use Docker:

```bash
docker run -d -p 27017:27017 --name mongo mongo:latest
```

Update your `MONGO_URI` in `config.yaml` to match your host.

---

## 📦 Installation (with `uv`)

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Run your project (example entrypoint):

   ```bash
   uv run python '.\main with stt.py'
   ```

---

## 📂 Folder Structure

```
jarvis
    ├── .gitignore
    ├── README.md
    ├── example.yaml
    ├── main with memory.py
    ├── main with stt and wakeword.py
    ├── main with stt.py
    ├── memory
    │   ├── memory.py
    │   └── memory_utils.py
    ├── pyproject.toml
    ├── react_prompt.py
    ├── robots
    │   └── spider_bot.py
    ├── stt
    │   ├── test_stt.py
    │   ├── vosk-model-small-en-us-0.15  # Place vosk here
    │   └── wakeword.py
    ├── tools
    │   ├── system_tools.py
    │   ├── tools.py
    │   ├── tools_list.py
    │   └── weather.py
    └── tts
        ├── tts.py
        └── your_ref.wav # Your reference audio here
```

---