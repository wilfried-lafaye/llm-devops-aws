"""
CRUD operations for Air Quality data
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from app.models import AirQualityRecord
from app.schemas import AirQualityCreate, AirQualityUpdate


def get_records(
    db: Session,
    commune: Optional[str] = None,
    region: Optional[str] = None,
    annee: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AirQualityRecord]:
    """Get air quality records with optional filters"""
    query = db.query(AirQualityRecord)
    
    if commune:
        query = query.filter(AirQualityRecord.commune.ilike(f"%{commune}%"))
    if region:
        query = query.filter(AirQualityRecord.region.ilike(f"%{region}%"))
    if annee:
        query = query.filter(AirQualityRecord.annee == annee)
    
    return query.order_by(desc(AirQualityRecord.annee)).offset(skip).limit(limit).all()


def get_record_by_id(db: Session, record_id: int) -> Optional[AirQualityRecord]:
    """Get a single record by ID"""
    return db.query(AirQualityRecord).filter(AirQualityRecord.id == record_id).first()


def get_total_count(
    db: Session,
    commune: Optional[str] = None,
    region: Optional[str] = None,
    annee: Optional[int] = None
) -> int:
    """Get total count of records with filters"""
    query = db.query(func.count(AirQualityRecord.id))
    
    if commune:
        query = query.filter(AirQualityRecord.commune.ilike(f"%{commune}%"))
    if region:
        query = query.filter(AirQualityRecord.region.ilike(f"%{region}%"))
    if annee:
        query = query.filter(AirQualityRecord.annee == annee)
    
    return query.scalar()


def create_record(db: Session, record: AirQualityCreate) -> AirQualityRecord:
    """Create a new air quality record"""
    db_record = AirQualityRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def update_record(
    db: Session,
    record_id: int,
    record_update: AirQualityUpdate
) -> Optional[AirQualityRecord]:
    """Update an existing record"""
    db_record = get_record_by_id(db, record_id)
    if not db_record:
        return None
    
    update_data = record_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record


def delete_record(db: Session, record_id: int) -> bool:
    """Delete a record by ID"""
    db_record = get_record_by_id(db, record_id)
    if not db_record:
        return False
    
    db.delete(db_record)
    db.commit()
    return True


def get_regions(db: Session) -> List[str]:
    """Get list of unique regions"""
    results = db.query(AirQualityRecord.region).distinct().order_by(AirQualityRecord.region).all()
    return [r[0] for r in results]


def get_communes(db: Session, region: Optional[str] = None) -> List[str]:
    """Get list of unique communes"""
    query = db.query(AirQualityRecord.commune).distinct()
    if region:
        query = query.filter(AirQualityRecord.region == region)
    results = query.order_by(AirQualityRecord.commune).all()
    return [c[0] for c in results]


def get_years(db: Session) -> List[int]:
    """Get list of available years"""
    results = db.query(AirQualityRecord.annee).distinct().order_by(desc(AirQualityRecord.annee)).all()
    return [y[0] for y in results]


def get_stats_by_region(db: Session, region: str, annee: Optional[int] = None) -> dict:
    """Get aggregated statistics for a region"""
    query = db.query(
        func.count(AirQualityRecord.id).label('count'),
        func.avg(AirQualityRecord.no2).label('avg_no2'),
        func.avg(AirQualityRecord.pm10).label('avg_pm10'),
        func.avg(AirQualityRecord.pm25).label('avg_pm25'),
        func.avg(AirQualityRecord.o3).label('avg_o3'),
        func.max(AirQualityRecord.no2).label('max_no2'),
        func.max(AirQualityRecord.pm10).label('max_pm10'),
        func.min(AirQualityRecord.no2).label('min_no2'),
        func.min(AirQualityRecord.pm10).label('min_pm10'),
    ).filter(AirQualityRecord.region.ilike(f"%{region}%"))
    
    if annee:
        query = query.filter(AirQualityRecord.annee == annee)
    
    result = query.first()
    return {
        "region": region,
        "annee": annee,
        "count": result.count or 0,
        "avg_no2": round(result.avg_no2, 2) if result.avg_no2 else None,
        "avg_pm10": round(result.avg_pm10, 2) if result.avg_pm10 else None,
        "avg_pm25": round(result.avg_pm25, 2) if result.avg_pm25 else None,
        "avg_o3": round(result.avg_o3, 2) if result.avg_o3 else None,
        "max_no2": result.max_no2,
        "max_pm10": result.max_pm10,
        "min_no2": result.min_no2,
        "min_pm10": result.min_pm10,
    }


def get_stats_by_commune(db: Session, commune: str) -> dict:
    """Get aggregated statistics for a commune"""
    query = db.query(
        func.count(AirQualityRecord.id).label('count'),
        func.avg(AirQualityRecord.no2).label('avg_no2'),
        func.avg(AirQualityRecord.pm10).label('avg_pm10'),
        func.avg(AirQualityRecord.pm25).label('avg_pm25'),
        func.avg(AirQualityRecord.o3).label('avg_o3'),
    ).filter(AirQualityRecord.commune.ilike(f"%{commune}%"))
    
    result = query.first()
    return {
        "commune": commune,
        "count": result.count or 0,
        "avg_no2": round(result.avg_no2, 2) if result.avg_no2 else None,
        "avg_pm10": round(result.avg_pm10, 2) if result.avg_pm10 else None,
        "avg_pm25": round(result.avg_pm25, 2) if result.avg_pm25 else None,
        "avg_o3": round(result.avg_o3, 2) if result.avg_o3 else None,
    }


def get_pollutant_trend(
    db: Session,
    pollutant: str,
    region: Optional[str] = None,
    commune: Optional[str] = None
) -> List[dict]:
    """Get trend of a specific pollutant over years"""
    pollutant_column = getattr(AirQualityRecord, pollutant, None)
    if not pollutant_column:
        return []
    
    query = db.query(
        AirQualityRecord.annee,
        func.avg(pollutant_column).label('value')
    )
    
    if region:
        query = query.filter(AirQualityRecord.region.ilike(f"%{region}%"))
    if commune:
        query = query.filter(AirQualityRecord.commune.ilike(f"%{commune}%"))
    
    results = query.group_by(AirQualityRecord.annee).order_by(AirQualityRecord.annee).all()
    
    return [
        {"annee": r.annee, "value": round(r.value, 2) if r.value else None}
        for r in results
    ]
