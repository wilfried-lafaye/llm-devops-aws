"""
Database configuration and utilities
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, AirQualityRecord

logger = logging.getLogger(__name__)

# Database URL from environment variable or default to SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/air_quality.db"
)

# Handle PostgreSQL URL format for SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def load_sample_data():
    """Load sample data if database is empty"""
    db = SessionLocal()
    try:
        # Check if data already exists
        count = db.query(AirQualityRecord).count()
        if count > 0:
            logger.info(f"Database already contains {count} records")
            return
        
        # Sample data for demonstration
        sample_data = [
            # Île-de-France
            {"commune": "Paris", "code_insee": "75056", "region": "Île-de-France", "departement": "Paris", "annee": 2020, "no2": 32.5, "pm10": 22.1, "pm25": 14.2, "o3": 45.3, "latitude": 48.8566, "longitude": 2.3522},
            {"commune": "Paris", "code_insee": "75056", "region": "Île-de-France", "departement": "Paris", "annee": 2021, "no2": 28.3, "pm10": 20.5, "pm25": 12.8, "o3": 48.1, "latitude": 48.8566, "longitude": 2.3522},
            {"commune": "Paris", "code_insee": "75056", "region": "Île-de-France", "departement": "Paris", "annee": 2022, "no2": 25.1, "pm10": 18.9, "pm25": 11.5, "o3": 51.2, "latitude": 48.8566, "longitude": 2.3522},
            {"commune": "Versailles", "code_insee": "78646", "region": "Île-de-France", "departement": "Yvelines", "annee": 2020, "no2": 18.2, "pm10": 16.8, "pm25": 10.5, "o3": 52.1, "latitude": 48.8014, "longitude": 2.1301},
            {"commune": "Versailles", "code_insee": "78646", "region": "Île-de-France", "departement": "Yvelines", "annee": 2021, "no2": 16.5, "pm10": 15.2, "pm25": 9.8, "o3": 54.3, "latitude": 48.8014, "longitude": 2.1301},
            {"commune": "Versailles", "code_insee": "78646", "region": "Île-de-France", "departement": "Yvelines", "annee": 2022, "no2": 14.8, "pm10": 14.1, "pm25": 9.1, "o3": 55.8, "latitude": 48.8014, "longitude": 2.1301},
            # Auvergne-Rhône-Alpes
            {"commune": "Lyon", "code_insee": "69123", "region": "Auvergne-Rhône-Alpes", "departement": "Rhône", "annee": 2020, "no2": 28.4, "pm10": 20.3, "pm25": 13.1, "o3": 48.5, "latitude": 45.7640, "longitude": 4.8357},
            {"commune": "Lyon", "code_insee": "69123", "region": "Auvergne-Rhône-Alpes", "departement": "Rhône", "annee": 2021, "no2": 25.2, "pm10": 18.7, "pm25": 11.8, "o3": 50.2, "latitude": 45.7640, "longitude": 4.8357},
            {"commune": "Lyon", "code_insee": "69123", "region": "Auvergne-Rhône-Alpes", "departement": "Rhône", "annee": 2022, "no2": 22.8, "pm10": 17.2, "pm25": 10.9, "o3": 52.8, "latitude": 45.7640, "longitude": 4.8357},
            {"commune": "Grenoble", "code_insee": "38185", "region": "Auvergne-Rhône-Alpes", "departement": "Isère", "annee": 2020, "no2": 24.1, "pm10": 19.5, "pm25": 12.8, "o3": 46.2, "latitude": 45.1885, "longitude": 5.7245},
            {"commune": "Grenoble", "code_insee": "38185", "region": "Auvergne-Rhône-Alpes", "departement": "Isère", "annee": 2021, "no2": 21.8, "pm10": 17.8, "pm25": 11.5, "o3": 48.9, "latitude": 45.1885, "longitude": 5.7245},
            {"commune": "Grenoble", "code_insee": "38185", "region": "Auvergne-Rhône-Alpes", "departement": "Isère", "annee": 2022, "no2": 19.5, "pm10": 16.2, "pm25": 10.3, "o3": 51.3, "latitude": 45.1885, "longitude": 5.7245},
            # Provence-Alpes-Côte d'Azur
            {"commune": "Marseille", "code_insee": "13055", "region": "Provence-Alpes-Côte d'Azur", "departement": "Bouches-du-Rhône", "annee": 2020, "no2": 30.2, "pm10": 24.5, "pm25": 15.8, "o3": 58.3, "latitude": 43.2965, "longitude": 5.3698},
            {"commune": "Marseille", "code_insee": "13055", "region": "Provence-Alpes-Côte d'Azur", "departement": "Bouches-du-Rhône", "annee": 2021, "no2": 27.5, "pm10": 22.1, "pm25": 14.2, "o3": 61.2, "latitude": 43.2965, "longitude": 5.3698},
            {"commune": "Marseille", "code_insee": "13055", "region": "Provence-Alpes-Côte d'Azur", "departement": "Bouches-du-Rhône", "annee": 2022, "no2": 24.8, "pm10": 20.5, "pm25": 13.1, "o3": 63.8, "latitude": 43.2965, "longitude": 5.3698},
            {"commune": "Nice", "code_insee": "06088", "region": "Provence-Alpes-Côte d'Azur", "departement": "Alpes-Maritimes", "annee": 2020, "no2": 26.8, "pm10": 21.2, "pm25": 13.5, "o3": 62.1, "latitude": 43.7102, "longitude": 7.2620},
            {"commune": "Nice", "code_insee": "06088", "region": "Provence-Alpes-Côte d'Azur", "departement": "Alpes-Maritimes", "annee": 2021, "no2": 24.2, "pm10": 19.5, "pm25": 12.3, "o3": 64.5, "latitude": 43.7102, "longitude": 7.2620},
            {"commune": "Nice", "code_insee": "06088", "region": "Provence-Alpes-Côte d'Azur", "departement": "Alpes-Maritimes", "annee": 2022, "no2": 21.8, "pm10": 18.1, "pm25": 11.5, "o3": 66.2, "latitude": 43.7102, "longitude": 7.2620},
            # Nouvelle-Aquitaine
            {"commune": "Bordeaux", "code_insee": "33063", "region": "Nouvelle-Aquitaine", "departement": "Gironde", "annee": 2020, "no2": 22.5, "pm10": 17.8, "pm25": 11.2, "o3": 49.5, "latitude": 44.8378, "longitude": -0.5792},
            {"commune": "Bordeaux", "code_insee": "33063", "region": "Nouvelle-Aquitaine", "departement": "Gironde", "annee": 2021, "no2": 20.1, "pm10": 16.2, "pm25": 10.1, "o3": 51.8, "latitude": 44.8378, "longitude": -0.5792},
            {"commune": "Bordeaux", "code_insee": "33063", "region": "Nouvelle-Aquitaine", "departement": "Gironde", "annee": 2022, "no2": 18.2, "pm10": 14.8, "pm25": 9.2, "o3": 53.5, "latitude": 44.8378, "longitude": -0.5792},
            # Occitanie
            {"commune": "Toulouse", "code_insee": "31555", "region": "Occitanie", "departement": "Haute-Garonne", "annee": 2020, "no2": 24.8, "pm10": 18.5, "pm25": 11.8, "o3": 52.3, "latitude": 43.6047, "longitude": 1.4442},
            {"commune": "Toulouse", "code_insee": "31555", "region": "Occitanie", "departement": "Haute-Garonne", "annee": 2021, "no2": 22.3, "pm10": 16.9, "pm25": 10.6, "o3": 54.8, "latitude": 43.6047, "longitude": 1.4442},
            {"commune": "Toulouse", "code_insee": "31555", "region": "Occitanie", "departement": "Haute-Garonne", "annee": 2022, "no2": 20.1, "pm10": 15.5, "pm25": 9.8, "o3": 56.5, "latitude": 43.6047, "longitude": 1.4442},
            {"commune": "Montpellier", "code_insee": "34172", "region": "Occitanie", "departement": "Hérault", "annee": 2020, "no2": 21.5, "pm10": 17.2, "pm25": 10.8, "o3": 55.8, "latitude": 43.6108, "longitude": 3.8767},
            {"commune": "Montpellier", "code_insee": "34172", "region": "Occitanie", "departement": "Hérault", "annee": 2021, "no2": 19.2, "pm10": 15.8, "pm25": 9.8, "o3": 58.2, "latitude": 43.6108, "longitude": 3.8767},
            {"commune": "Montpellier", "code_insee": "34172", "region": "Occitanie", "departement": "Hérault", "annee": 2022, "no2": 17.5, "pm10": 14.5, "pm25": 9.1, "o3": 60.1, "latitude": 43.6108, "longitude": 3.8767},
            # Hauts-de-France
            {"commune": "Lille", "code_insee": "59350", "region": "Hauts-de-France", "departement": "Nord", "annee": 2020, "no2": 26.2, "pm10": 21.5, "pm25": 14.1, "o3": 42.5, "latitude": 50.6292, "longitude": 3.0573},
            {"commune": "Lille", "code_insee": "59350", "region": "Hauts-de-France", "departement": "Nord", "annee": 2021, "no2": 23.8, "pm10": 19.8, "pm25": 12.8, "o3": 44.8, "latitude": 50.6292, "longitude": 3.0573},
            {"commune": "Lille", "code_insee": "59350", "region": "Hauts-de-France", "departement": "Nord", "annee": 2022, "no2": 21.5, "pm10": 18.2, "pm25": 11.8, "o3": 46.5, "latitude": 50.6292, "longitude": 3.0573},
            # Grand Est
            {"commune": "Strasbourg", "code_insee": "67482", "region": "Grand Est", "departement": "Bas-Rhin", "annee": 2020, "no2": 25.5, "pm10": 20.8, "pm25": 13.5, "o3": 44.2, "latitude": 48.5734, "longitude": 7.7521},
            {"commune": "Strasbourg", "code_insee": "67482", "region": "Grand Est", "departement": "Bas-Rhin", "annee": 2021, "no2": 23.1, "pm10": 19.2, "pm25": 12.3, "o3": 46.5, "latitude": 48.5734, "longitude": 7.7521},
            {"commune": "Strasbourg", "code_insee": "67482", "region": "Grand Est", "departement": "Bas-Rhin", "annee": 2022, "no2": 20.8, "pm10": 17.8, "pm25": 11.2, "o3": 48.2, "latitude": 48.5734, "longitude": 7.7521},
            # Pays de la Loire
            {"commune": "Nantes", "code_insee": "44109", "region": "Pays de la Loire", "departement": "Loire-Atlantique", "annee": 2020, "no2": 20.5, "pm10": 16.2, "pm25": 10.2, "o3": 47.8, "latitude": 47.2184, "longitude": -1.5536},
            {"commune": "Nantes", "code_insee": "44109", "region": "Pays de la Loire", "departement": "Loire-Atlantique", "annee": 2021, "no2": 18.2, "pm10": 14.8, "pm25": 9.2, "o3": 49.5, "latitude": 47.2184, "longitude": -1.5536},
            {"commune": "Nantes", "code_insee": "44109", "region": "Pays de la Loire", "departement": "Loire-Atlantique", "annee": 2022, "no2": 16.5, "pm10": 13.5, "pm25": 8.5, "o3": 51.2, "latitude": 47.2184, "longitude": -1.5536},
            # Bretagne
            {"commune": "Rennes", "code_insee": "35238", "region": "Bretagne", "departement": "Ille-et-Vilaine", "annee": 2020, "no2": 18.8, "pm10": 14.5, "pm25": 9.2, "o3": 45.5, "latitude": 48.1173, "longitude": -1.6778},
            {"commune": "Rennes", "code_insee": "35238", "region": "Bretagne", "departement": "Ille-et-Vilaine", "annee": 2021, "no2": 16.5, "pm10": 13.2, "pm25": 8.3, "o3": 47.2, "latitude": 48.1173, "longitude": -1.6778},
            {"commune": "Rennes", "code_insee": "35238", "region": "Bretagne", "departement": "Ille-et-Vilaine", "annee": 2022, "no2": 14.8, "pm10": 12.1, "pm25": 7.6, "o3": 48.8, "latitude": 48.1173, "longitude": -1.6778},
        ]
        
        # Insert sample data
        for record_data in sample_data:
            record = AirQualityRecord(**record_data)
            db.add(record)
        
        db.commit()
        logger.info(f"Loaded {len(sample_data)} sample records")
        
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        db.rollback()
    finally:
        db.close()
