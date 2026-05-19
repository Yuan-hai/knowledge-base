"""Settings endpoints - model selection & upload folder config."""

from fastapi import APIRouter
from config import load_settings, save_settings, AVAILABLE_MODELS
from models.schemas import SettingsUpdate, SettingsResponse, ModelInfo

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
async def get_settings():
    s = load_settings()
    return SettingsResponse(
        selected_model=s["selected_model"],
        upload_folder=s["upload_folder"],
        api_key=s["api_key"],
        api_base_url=s["api_base_url"],
        api_embedding_url=s["api_embedding_url"],
        embedding_model=s["embedding_model"],
        available_models=[ModelInfo(**m) for m in AVAILABLE_MODELS],
    )


@router.put("", response_model=SettingsResponse)
async def update_settings(body: SettingsUpdate):
    s = load_settings()
    if body.selected_model is not None:
        s["selected_model"] = body.selected_model.strip()
    if body.upload_folder is not None:
        s["upload_folder"] = body.upload_folder.strip()
    if body.api_key is not None:
        s["api_key"] = body.api_key.strip()
    if body.api_base_url is not None:
        s["api_base_url"] = body.api_base_url.strip()
    if body.api_embedding_url is not None:
        s["api_embedding_url"] = body.api_embedding_url.strip()
    if body.embedding_model is not None:
        s["embedding_model"] = body.embedding_model.strip()
    if body.models is not None:
        s["models"] = [m.model_dump() for m in body.models]
    save_settings(s)
    # Reload to pick up merged custom models
    s = load_settings()
    return SettingsResponse(
        selected_model=s["selected_model"],
        upload_folder=s["upload_folder"],
        api_key=s["api_key"],
        api_base_url=s["api_base_url"],
        api_embedding_url=s["api_embedding_url"],
        embedding_model=s["embedding_model"],
        available_models=[ModelInfo(**m) for m in AVAILABLE_MODELS],
    )


@router.get("/models")
async def get_models():
    return {"models": AVAILABLE_MODELS}
