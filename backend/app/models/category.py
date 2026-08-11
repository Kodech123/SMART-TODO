from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

DEFAULT_CATEGORIES = [
    {"category_name": "Academic", "color_hex": "#1976D2", "icon_name": "school"},
    {"category_name": "Work", "color_hex": "#F57C00", "icon_name": "work"},
    {"category_name": "Personal", "color_hex": "#388E3C", "icon_name": "person"},
    {"category_name": "Health", "color_hex": "#E91E63", "icon_name": "favorite"},
]


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("user_id", "category_name", name="uq_category_per_user"),)

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    color_hex: Mapped[str] = mapped_column(String(7), nullable=False, default="#2E5C8A", server_default="#2E5C8A")
    icon_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    user: Mapped["User"] = relationship(back_populates="categories")
    tasks: Mapped[list["Task"]] = relationship(back_populates="category")
