"""Library backend configuration. Settings persist to data/settings.json."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_EMBEDDING_URL = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
DASHSCOPE_EMBEDDING_MODEL = "text-embedding-v3"
DASHSCOPE_CHAT_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

AVAILABLE_MODELS = [
    {"id": "qwen-turbo", "name": "Qwen Turbo (fast)"},
    {"id": "qwen-plus", "name": "Qwen Plus (balanced)"},
    {"id": "qwen-max", "name": "Qwen Max (powerful)"},
    {"id": "qwen3.6-plus", "name": "Qwen 3.6 Plus"},
]

DEFAULT_SETTINGS = {
    "selected_model": "qwen-plus",
    "upload_folder": "G:/documents/knowledge-base",
}


def load_settings() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {**DEFAULT_SETTINGS}


def save_settings(settings: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
