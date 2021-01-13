from sqlalchemy import Column
from sqlalchemy.types import Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import ForeignKey
from datetime import datetime, timezone
import uuid

Base = declarative_base()

class Urls(Base):
    __tablename__ = "urls"

    url_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    url = Column(Text(), nullable=False, unique = True)
    kafka_offset = Column(Integer(), nullable=False)
    kafka_produce_time = Column(DateTime(timezone=True))

    def __repr__(self):
        return '<url {}>'.format(self.url)

class Ngrams(Base):
    __tablename__ = "ngrams"

    fivegram_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    key = Column(String(145), index=True, nullable=False)
    prediction = Column(String(45), nullable=False)
    n =Column(Integer, nullable=False)
    url_id = Column(UUID(as_uuid=True), ForeignKey("urls.url_id"), nullable=False)


    def __repr__(self):
        return '5 <key {}>, <prediction {}>'.format(self.key, self.prediction)                    




