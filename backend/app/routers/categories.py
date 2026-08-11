from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


def _get_owned_category(db: Session, category_id: int, user_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None or category.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.get("", response_model=list[CategoryResponse])
def list_categories(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Category]:
    return (
        db.query(Category)
        .filter(Category.user_id == current_user.user_id)
        .order_by(Category.is_default.desc(), Category.category_name)
        .all()
    )


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Category:
    existing = (
        db.query(Category)
        .filter(Category.user_id == current_user.user_id, Category.category_name == payload.category_name)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")

    category = Category(user_id=current_user.user_id, **payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Category:
    category = _get_owned_category(db, category_id, current_user.user_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    category = _get_owned_category(db, category_id, current_user.user_id)
    if category.is_default:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete a default category")
    db.delete(category)
    db.commit()
