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
        available_models=[ModelInfo(**m) for m in AVAILABLE_MODELS],
    )


@router.put("", response_model=SettingsResponse)
async def update_settings(body: SettingsUpdate):
    s = load_settings()
    if body.selected_model is not None:
        s["selected_model"] = body.selected_model
    if body.upload_folder is not None:
        s["upload_folder"] = body.upload_folder
    save_settings(s)
    return SettingsResponse(
        selected_model=s["selected_model"],
        upload_folder=s["upload_folder"],
        available_models=[ModelInfo(**m) for m in AVAILABLE_MODELS],
    )


@router.get("/models")
async def get_models():
    return {"models": AVAILABLE_MODELS}
