"""
Pydantic Schemas for API validation and serialization
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AirQualityBase(BaseModel):
    """Base schema for air quality data"""
    commune: str = Field(..., min_length=1, max_length=100, description="Nom de la commune")
    code_insee: str = Field(..., min_length=5, max_length=10, description="Code INSEE")
    region: str = Field(..., min_length=1, max_length=100, description="Région")
    departement: str = Field(..., min_length=1, max_length=100, description="Département")
    annee: int = Field(..., ge=2000, le=2030, description="Année de mesure")
    no2: Optional[float] = Field(None, ge=0, description="NO2 (µg/m³)")
    pm10: Optional[float] = Field(None, ge=0, description="PM10 (µg/m³)")
    pm25: Optional[float] = Field(None, ge=0, description="PM2.5 (µg/m³)")
    o3: Optional[float] = Field(None, ge=0, description="O3 (µg/m³)")
    somo35: Optional[float] = Field(None, ge=0, description="SOMO35 (µg/m³.jour)")
    aot40: Optional[float] = Field(None, ge=0, description="AOT40 (µg/m³.heure)")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class AirQualityCreate(AirQualityBase):
    """Schema for creating air quality records"""
    pass


class AirQualityUpdate(BaseModel):
    """Schema for updating air quality records"""
    commune: Optional[str] = None
    region: Optional[str] = None
    departement: Optional[str] = None
    no2: Optional[float] = None
    pm10: Optional[float] = None
    pm25: Optional[float] = None
    o3: Optional[float] = None
    somo35: Optional[float] = None
    aot40: Optional[float] = None


class AirQualityResponse(AirQualityBase):
    """Schema for air quality response"""
    id: int
    
    class Config:
        from_attributes = True


class AirQualityListResponse(BaseModel):
    """Schema for paginated list response"""
    total: int
    page: int
    page_size: int
    data: List[AirQualityResponse]


class StatsResponse(BaseModel):
    """Schema for statistics response"""
    region: Optional[str] = None
    commune: Optional[str] = None
    annee: Optional[int] = None
    count: int
    avg_no2: Optional[float] = None
    avg_pm10: Optional[float] = None
    avg_pm25: Optional[float] = None
    avg_o3: Optional[float] = None
    max_no2: Optional[float] = None
    max_pm10: Optional[float] = None
    min_no2: Optional[float] = None
    min_pm10: Optional[float] = None


class RegionListResponse(BaseModel):
    """List of regions"""
    regions: List[str]


class YearListResponse(BaseModel):
    """List of available years"""
    years: List[int]


class PollutantTrend(BaseModel):
    """Pollutant trend over time"""
    annee: int
    value: Optional[float]


class TrendResponse(BaseModel):
    """Trend response for a pollutant"""
    pollutant: str
    region: Optional[str] = None
    commune: Optional[str] = None
    data: List[PollutantTrend]
