import re
from tools.tools import remember_fact

# Pattern to detect key-value pairs in natural language
FACT_PATTERNS = [
    re.compile(r"(?i)my (?P<key>[\w\s]+?) is (?P<value>.+?)(?:[.?!]|$)"),
    re.compile(r"(?i)i (?:like|love|prefer) (?P<key>[\w\s]+): (?P<value>.+?)(?:[.?!]|$)"),
]

def auto_remember_from_input(text: str):
    """Extracts facts from user input and stores them in memory."""
    for pattern in FACT_PATTERNS:
        match = pattern.search(text)
        if match:
            key = match.group("key").strip().lower()
            value = match.group("value").strip()
            try:
                remember_fact(f"{key}: {value}")
                print(f"[Auto-Memory] Remembered -> {key}: {value}")
            except Exception as e:
                print(f"[Auto-Memory] Failed to remember fact: {e}")
