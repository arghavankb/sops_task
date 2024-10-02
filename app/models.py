from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, LargeBinary, func
import datetime


class Base(DeclarativeBase):
    pass

class Image(Base):
    __tablename__ = "image"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    image_data: Mapped[bytes] = mapped_column(LargeBinary)
    search_term: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
