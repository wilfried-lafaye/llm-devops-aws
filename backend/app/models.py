"""
SQLAlchemy Models for Air Quality Data
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AirQualityRecord(Base):
    """Model for air quality measurements"""
    __tablename__ = "air_quality"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    commune = Column(String(100), nullable=False, index=True)
    code_insee = Column(String(10), nullable=False, index=True)
    region = Column(String(100), nullable=False, index=True)
    departement = Column(String(100), nullable=False)
    annee = Column(Integer, nullable=False, index=True)
    
    # Pollutants
    no2 = Column(Float, nullable=True)  # Dioxyde d'azote (µg/m³)
    pm10 = Column(Float, nullable=True)  # Particules PM10 (µg/m³)
    pm25 = Column(Float, nullable=True)  # Particules PM2.5 (µg/m³)
    o3 = Column(Float, nullable=True)  # Ozone (µg/m³)
    somo35 = Column(Float, nullable=True)  # SOMO35 (µg/m³.jour)
    aot40 = Column(Float, nullable=True)  # AOT40 (µg/m³.heure)
    
    # Coordinates
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_commune_annee', 'commune', 'annee'),
        Index('idx_region_annee', 'region', 'annee'),
    )
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "commune": self.commune,
            "code_insee": self.code_insee,
            "region": self.region,
            "departement": self.departement,
            "annee": self.annee,
            "no2": self.no2,
            "pm10": self.pm10,
            "pm25": self.pm25,
            "o3": self.o3,
            "somo35": self.somo35,
            "aot40": self.aot40,
            "latitude": self.latitude,
            "longitude": self.longitude
        }
