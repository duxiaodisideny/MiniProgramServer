from sqlalchemy import Column, String
from app.models.base import db, Base  # noqa


class VerifiedCompany(Base):
    __tablename__ = 'verified_company_list'

    companyName = Column('company_name', String(32))
