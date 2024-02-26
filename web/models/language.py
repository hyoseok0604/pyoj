from sqlalchemy.orm import Mapped, mapped_column

from web.models.base import BaseModel


class Language(BaseModel):
    __tablename__ = "language"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    display_name: Mapped[str] = mapped_column(unique=True)
    filename: Mapped[str]
    compile_command: Mapped[str]
    execute_command: Mapped[str]
