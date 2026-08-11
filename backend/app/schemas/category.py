from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    category_name: str = Field(min_length=1, max_length=100)
    color_hex: str = Field(default="#2E5C8A", pattern=r"^#[0-9A-Fa-f]{6}$")
    icon_name: str | None = None


class CategoryUpdate(BaseModel):
    category_name: str | None = Field(default=None, min_length=1, max_length=100)
    color_hex: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon_name: str | None = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    category_name: str
    color_hex: str
    icon_name: str | None
    is_default: bool
    created_at: datetime
