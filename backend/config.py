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

BASE_MODELS = [
    {"id": "qwen-turbo", "name": "Qwen Turbo (fast)"},
    {"id": "qwen-plus", "name": "Qwen Plus (balanced)"},
    {"id": "qwen-max", "name": "Qwen Max (powerful)"},
    {"id": "qwen3.6-plus", "name": "Qwen 3.6 Plus"},
    {"id": "deepseek-chat", "name": "DeepSeek Chat"},
    {"id": "deepseek-reasoner", "name": "DeepSeek Reasoner"},
]

AVAILABLE_MODELS = list(BASE_MODELS)

DEFAULT_SETTINGS = {
    "selected_model": "qwen-plus",
    "upload_folder": "G:/documents/knowledge-base",
    "api_key": "",
    "api_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    "api_embedding_url": "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding",
    "embedding_model": "text-embedding-v3",
}


def load_settings() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    merged = {**DEFAULT_SETTINGS}
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            merged.update(json.load(f))
    # Rebuild AVAILABLE_MODELS from base + custom
    AVAILABLE_MODELS.clear()
    AVAILABLE_MODELS.extend(BASE_MODELS)
    custom_models = merged.get("models", [])
    if custom_models:
        existing_ids = {m["id"] for m in AVAILABLE_MODELS}
        for m in custom_models:
            if m.get("id") and m["id"] not in existing_ids:
                AVAILABLE_MODELS.append({"id": m["id"], "name": m.get("name", m["id"])})
                existing_ids.add(m["id"])
    return merged


def save_settings(settings: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
