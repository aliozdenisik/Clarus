from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key_validator import get_current_user_flexible
from app.db import get_db
from app.models import UserPreferences

router = APIRouter()


class PreferencesUpdate(BaseModel):
    theme: Optional[str] = Field(None, pattern="^(light|dark|system)$")
    language: Optional[str] = Field(None, pattern="^(tr|en|ar)$")
    default_search_source: Optional[str] = Field(None, pattern="^(quran|bible|all)$")
    default_bible_testament: Optional[str] = Field(None, pattern="^(ot|nt|apocrypha|all)$")
    results_per_page: Optional[int] = Field(None, ge=5, le=50)
    enable_streaming: Optional[bool] = None
    enable_multi_agent: Optional[bool] = None
    custom_settings: Optional[dict] = None


class PreferencesResponse(BaseModel):
    success: bool = True
    data: dict


def _preferences_to_dict(prefs: UserPreferences) -> dict:
    return {
        "theme": prefs.theme,
        "language": prefs.language,
        "default_search_source": prefs.default_search_source,
        "default_bible_testament": prefs.default_bible_testament,
        "results_per_page": prefs.results_per_page,
        "enable_streaming": prefs.enable_streaming,
        "enable_multi_agent": prefs.enable_multi_agent,
        "custom_settings": prefs.custom_settings,
        "updated_at": prefs.updated_at.isoformat() if prefs.updated_at else None,
    }


def _get_default_preferences() -> dict:
    return {
        "theme": "system",
        "language": "tr",
        "default_search_source": "quran",
        "default_bible_testament": None,
        "results_per_page": 10,
        "enable_streaming": True,
        "enable_multi_agent": True,
        "custom_settings": None,
        "updated_at": None,
    }


@router.get("/", response_model=PreferencesResponse)
async def get_preferences(
    current_user: Dict[str, Any] = Depends(get_current_user_flexible),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user["id"])
    )
    prefs = result.scalar_one_or_none()

    if prefs:
        return PreferencesResponse(data=_preferences_to_dict(prefs))

    return PreferencesResponse(data=_get_default_preferences())


@router.put("/", response_model=PreferencesResponse)
async def update_preferences(
    updates: PreferencesUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user_flexible),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user["id"])
    )
    prefs = result.scalar_one_or_none()

    if not prefs:
        prefs = UserPreferences(user_id=current_user["id"])
        db.add(prefs)

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prefs, field, value)

    prefs.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(prefs)

    return PreferencesResponse(data=_preferences_to_dict(prefs))


@router.delete("/")
async def reset_preferences(
    current_user: Dict[str, Any] = Depends(get_current_user_flexible),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserPreferences).where(UserPreferences.user_id == current_user["id"])
    )
    prefs = result.scalar_one_or_none()

    if prefs:
        await db.delete(prefs)
        await db.commit()

    return {"success": True, "message": "Preferences reset to defaults"}
