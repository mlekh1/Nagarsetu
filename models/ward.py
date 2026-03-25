from sqlalchemy import Column, Integer, String
from geoalchemy2 import Geometry
from database import Base

class Ward(Base):
    __tablename__ = "wards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    polygon = Column(Geometry(geometry_type='POLYGON', srid=4326))