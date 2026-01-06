from sqlmodel import Session, select

from budy.schemas import Category


def create_category(*, session: Session, name: str, color: str = "white") -> Category:
    """Creates a new category."""
    category = Category(name=name, color=color)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def get_categories(*, session: Session) -> list[Category]:
    """Returns all categories."""
    return list(session.exec(select(Category)).all())


def delete_category(*, session: Session, category_id: int) -> bool:
    """Deletes a category by ID."""
    category = session.get(Category, category_id)
    if not category:
        return False
    session.delete(category)
    session.commit()
    return True
