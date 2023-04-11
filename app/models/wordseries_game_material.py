from sqlalchemy import Column, String
from app.models.base import db, Base  # noqa


class WordSeriesGameMaterial(Base):
    __tablename__ = 'words_series_game_material'

    content = Column('content', String(128))
    contentType = Column('content_type', String(32))
    option_a = Column('option_word_a', String(128), index=True)
    option_b = Column('option_word_b', String(128), index=True)
    option_c = Column('option_word_c', String(128), index=True)
    option_d = Column('option_word_d', String(128), index=True)
    option_e = Column('option_word_e', String(128), index=True)
    option_f = Column('option_word_f', String(128), index=True)