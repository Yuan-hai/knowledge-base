"""Pydantic models for Library API request/response validation."""

from typing import List, Optional
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


class ModelInfo(BaseModel):
    id: str
    name: str


class SettingsUpdate(BaseModel):
    selected_model: Optional[str] = None
    upload_folder: Optional[str] = None
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    api_embedding_url: Optional[str] = None
    embedding_model: Optional[str] = None
    models: Optional[List[ModelInfo]] = None


class SettingsResponse(BaseModel):
    selected_model: str
    upload_folder: str
    api_key: str
    api_base_url: str
    api_embedding_url: str
    embedding_model: str
    available_models: List[ModelInfo]
