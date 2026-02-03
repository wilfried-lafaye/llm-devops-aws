"""
API Router for Air Quality CRUD operations
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app import crud
from app.schemas import (
    AirQualityResponse,
    AirQualityCreate,
    AirQualityUpdate,
    AirQualityListResponse,
    RegionListResponse,
    YearListResponse
)

router = APIRouter()


@router.get("/records", response_model=AirQualityListResponse)
def get_records(
    commune: Optional[str] = Query(None, description="Filter by commune name"),
    region: Optional[str] = Query(None, description="Filter by region"),
    annee: Optional[int] = Query(None, description="Filter by year"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get air quality records with optional filters and pagination.
    
    - **commune**: Filter by commune name (partial match)
    - **region**: Filter by region name (partial match)
    - **annee**: Filter by year (exact match)
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 50, max: 1000)
    """
    skip = (page - 1) * page_size
    
    records = crud.get_records(
        db=db,
        commune=commune,
        region=region,
        annee=annee,
        skip=skip,
        limit=page_size
    )
    
    total = crud.get_total_count(db, commune=commune, region=region, annee=annee)
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": records
    }


@router.get("/records/{record_id}", response_model=AirQualityResponse)
def get_record(record_id: int, db: Session = Depends(get_db)):
    """Get a single air quality record by ID"""
    record = crud.get_record_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.post("/records", response_model=AirQualityResponse, status_code=201)
def create_record(record: AirQualityCreate, db: Session = Depends(get_db)):
    """
    Create a new air quality record.
    
    All pollutant values are in µg/m³.
    """
    return crud.create_record(db, record)


@router.put("/records/{record_id}", response_model=AirQualityResponse)
def update_record(
    record_id: int,
    record_update: AirQualityUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing air quality record"""
    updated = crud.update_record(db, record_id, record_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Record not found")
    return updated


@router.delete("/records/{record_id}", status_code=204)
def delete_record(record_id: int, db: Session = Depends(get_db)):
    """Delete an air quality record"""
    deleted = crud.delete_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
    return None


@router.get("/regions", response_model=RegionListResponse)
def get_regions(db: Session = Depends(get_db)):
    """Get list of all available regions"""
    regions = crud.get_regions(db)
    return {"regions": regions}


@router.get("/communes")
def get_communes(
    region: Optional[str] = Query(None, description="Filter by region"),
    db: Session = Depends(get_db)
):
    """Get list of all communes, optionally filtered by region"""
    communes = crud.get_communes(db, region=region)
    return {"communes": communes}


@router.get("/years", response_model=YearListResponse)
def get_years(db: Session = Depends(get_db)):
    """Get list of all available years"""
    years = crud.get_years(db)
    return {"years": years}
