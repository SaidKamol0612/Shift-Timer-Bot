from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    Mapped,
    mapped_column,
)
from utils.case_converter import camel_case_to_snake_case


class Base(DeclarativeBase):
    """
    Abstract base class for all SQLAlchemy models.

    Provides:
    - Automatic table naming using camel_case_to_snake_case + 's' suffix
    - Primary key 'id' column for all models
    """

    __abstract__ = True  # Prevent SQLAlchemy from creating a table for Base itself

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Automatically generate table name from class name.

        Converts CamelCase class name to snake_case and adds 's' suffix.
        Example:
            UserProfile -> user_profiles
        """
        return f"{camel_case_to_snake_case(cls.__name__)}s"

    # Common primary key column for all models
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        nullable=False
    )
