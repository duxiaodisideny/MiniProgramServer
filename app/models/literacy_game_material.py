from sqlalchemy import Column, String
from app.models.base import db, Base  # noqa


class LiteracyGameMaterial(Base):
    __tablename__ = 'literacy_game_material'

    content = Column('content', String(32))
    contentType = Column('content_type', String(32))
    wordImg = Column('word_img', String(128), index=True)
    pictogramsImg = Column('pictograms_img', String(128), index=True)