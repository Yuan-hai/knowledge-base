"""Pydantic models for Library API request/response validation."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentInfo(BaseModel):
    id: str
    filename: str
    created_at: str
    chunk_count: int = 0


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "qwen-plus"


class RagQueryRequest(BaseModel):
    query: str
    document_ids: List[str]
    model: str = "qwen-plus"
    top_k: int = Field(default=5, ge=1, le=20)


class SettingsUpdate(BaseModel):
    selected_model: Optional[str] = None
    upload_folder: Optional[str] = None


class ModelInfo(BaseModel):
    id: str
    name: str


class SettingsResponse(BaseModel):
    selected_model: str
    upload_folder: str
    available_models: List[ModelInfo]
