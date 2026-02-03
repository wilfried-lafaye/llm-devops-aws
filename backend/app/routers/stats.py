"""
API Router for Statistics and Analytics
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import crud
from app.schemas import StatsResponse, TrendResponse

router = APIRouter()


@router.get("/stats/region/{region}", response_model=StatsResponse)
def get_region_stats(
    region: str,
    annee: Optional[int] = Query(None, description="Filter by year"),
    db: Session = Depends(get_db)
):
    """
    Get aggregated statistics for a region.
    
    Returns average, min, and max values for all pollutants.
    """
    stats = crud.get_stats_by_region(db, region, annee)
    if stats["count"] == 0:
        raise HTTPException(status_code=404, detail=f"No data found for region: {region}")
    return stats


@router.get("/stats/commune/{commune}", response_model=StatsResponse)
def get_commune_stats(commune: str, db: Session = Depends(get_db)):
    """
    Get aggregated statistics for a commune.
    
    Returns average values for all pollutants across all years.
    """
    stats = crud.get_stats_by_commune(db, commune)
    if stats["count"] == 0:
        raise HTTPException(status_code=404, detail=f"No data found for commune: {commune}")
    return stats


@router.get("/trends/{pollutant}", response_model=TrendResponse)
def get_pollutant_trend(
    pollutant: str,
    region: Optional[str] = Query(None, description="Filter by region"),
    commune: Optional[str] = Query(None, description="Filter by commune"),
    db: Session = Depends(get_db)
):
    """
    Get trend of a specific pollutant over time.
    
    Valid pollutants: no2, pm10, pm25, o3, somo35, aot40
    """
    valid_pollutants = ["no2", "pm10", "pm25", "o3", "somo35", "aot40"]
    
    if pollutant.lower() not in valid_pollutants:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid pollutant. Valid options: {', '.join(valid_pollutants)}"
        )
    
    trend_data = crud.get_pollutant_trend(
        db,
        pollutant=pollutant.lower(),
        region=region,
        commune=commune
    )
    
    if not trend_data:
        raise HTTPException(status_code=404, detail="No trend data found")
    
    return {
        "pollutant": pollutant,
        "region": region,
        "commune": commune,
        "data": trend_data
    }


@router.get("/compare")
def compare_regions(
    regions: str = Query(..., description="Comma-separated list of regions"),
    annee: Optional[int] = Query(None, description="Filter by year"),
    db: Session = Depends(get_db)
):
    """
    Compare statistics across multiple regions.
    
    - **regions**: Comma-separated list of region names
    - **annee**: Optional year filter
    """
    region_list = [r.strip() for r in regions.split(",")]
    
    if len(region_list) < 2:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least 2 regions to compare"
        )
    
    results = []
    for region in region_list:
        stats = crud.get_stats_by_region(db, region, annee)
        if stats["count"] > 0:
            results.append(stats)
    
    if not results:
        raise HTTPException(status_code=404, detail="No data found for the specified regions")
    
    return {
        "comparison": results,
        "annee": annee
    }


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    """
    Get a summary of the entire dataset.
    
    Returns total records, available regions, years, and global averages.
    """
    from sqlalchemy import func
    from app.models import AirQualityRecord
    
    # Get counts
    total_records = db.query(func.count(AirQualityRecord.id)).scalar()
    total_regions = db.query(func.count(func.distinct(AirQualityRecord.region))).scalar()
    total_communes = db.query(func.count(func.distinct(AirQualityRecord.commune))).scalar()
    
    # Get averages
    averages = db.query(
        func.avg(AirQualityRecord.no2).label('avg_no2'),
        func.avg(AirQualityRecord.pm10).label('avg_pm10'),
        func.avg(AirQualityRecord.pm25).label('avg_pm25'),
        func.avg(AirQualityRecord.o3).label('avg_o3'),
    ).first()
    
    # Get year range
    years = crud.get_years(db)
    
    return {
        "total_records": total_records,
        "total_regions": total_regions,
        "total_communes": total_communes,
        "year_range": {
            "min": min(years) if years else None,
            "max": max(years) if years else None
        },
        "global_averages": {
            "no2": round(averages.avg_no2, 2) if averages.avg_no2 else None,
            "pm10": round(averages.avg_pm10, 2) if averages.avg_pm10 else None,
            "pm25": round(averages.avg_pm25, 2) if averages.avg_pm25 else None,
            "o3": round(averages.avg_o3, 2) if averages.avg_o3 else None,
        }
    }
