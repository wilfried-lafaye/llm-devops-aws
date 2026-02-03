"""
Unit Tests for Air Quality API
Run with: pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base, AirQualityRecord

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create test client with fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    
    # Add test data
    db = TestingSessionLocal()
    test_records = [
        AirQualityRecord(
            commune="Paris",
            code_insee="75056",
            region="Île-de-France",
            departement="Paris",
            annee=2020,
            no2=32.5,
            pm10=22.1,
            pm25=14.2,
            o3=45.3,
            latitude=48.8566,
            longitude=2.3522
        ),
        AirQualityRecord(
            commune="Paris",
            code_insee="75056",
            region="Île-de-France",
            departement="Paris",
            annee=2021,
            no2=28.3,
            pm10=20.5,
            pm25=12.8,
            o3=48.1,
            latitude=48.8566,
            longitude=2.3522
        ),
        AirQualityRecord(
            commune="Lyon",
            code_insee="69123",
            region="Auvergne-Rhône-Alpes",
            departement="Rhône",
            annee=2020,
            no2=28.4,
            pm10=20.3,
            pm25=13.1,
            o3=48.5,
            latitude=45.7640,
            longitude=4.8357
        ),
        AirQualityRecord(
            commune="Marseille",
            code_insee="13055",
            region="Provence-Alpes-Côte d'Azur",
            departement="Bouches-du-Rhône",
            annee=2020,
            no2=30.2,
            pm10=24.5,
            pm25=15.8,
            o3=58.3,
            latitude=43.2965,
            longitude=5.3698
        ),
    ]
    
    for record in test_records:
        db.add(record)
    db.commit()
    db.close()
    
    with TestClient(app) as test_client:
        yield test_client
    
    Base.metadata.drop_all(bind=engine)


# ============== Health Check Tests ==============

class TestHealthCheck:
    """Tests for health check endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["version"] == "1.0.0"
    
    def test_health_check(self, client):
        """Test health check returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


# ============== CRUD Tests ==============

class TestCRUDOperations:
    """Tests for CRUD operations"""
    
    def test_get_records(self, client):
        """Test getting all records"""
        response = client.get("/api/v1/records")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert data["total"] == 4
    
    def test_get_records_with_pagination(self, client):
        """Test pagination works correctly"""
        response = client.get("/api/v1/records?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2
    
    def test_get_records_filter_by_commune(self, client):
        """Test filtering by commune"""
        response = client.get("/api/v1/records?commune=Paris")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(r["commune"] == "Paris" for r in data["data"])
    
    def test_get_records_filter_by_region(self, client):
        """Test filtering by region"""
        response = client.get("/api/v1/records?region=Île-de-France")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
    
    def test_get_records_filter_by_year(self, client):
        """Test filtering by year"""
        response = client.get("/api/v1/records?annee=2020")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert all(r["annee"] == 2020 for r in data["data"])
    
    def test_get_single_record(self, client):
        """Test getting a single record by ID"""
        response = client.get("/api/v1/records/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["commune"] == "Paris"
    
    def test_get_nonexistent_record(self, client):
        """Test 404 for non-existent record"""
        response = client.get("/api/v1/records/999")
        assert response.status_code == 404
    
    def test_create_record(self, client):
        """Test creating a new record"""
        new_record = {
            "commune": "Bordeaux",
            "code_insee": "33063",
            "region": "Nouvelle-Aquitaine",
            "departement": "Gironde",
            "annee": 2022,
            "no2": 22.5,
            "pm10": 17.8,
            "pm25": 11.2,
            "o3": 49.5
        }
        response = client.post("/api/v1/records", json=new_record)
        assert response.status_code == 201
        data = response.json()
        assert data["commune"] == "Bordeaux"
        assert data["id"] is not None
    
    def test_create_record_validation_error(self, client):
        """Test validation error for invalid data"""
        invalid_record = {
            "commune": "",  # Empty commune should fail
            "code_insee": "33063",
            "region": "Nouvelle-Aquitaine",
            "departement": "Gironde",
            "annee": 2022
        }
        response = client.post("/api/v1/records", json=invalid_record)
        assert response.status_code == 422
    
    def test_update_record(self, client):
        """Test updating an existing record"""
        update_data = {"no2": 35.0}
        response = client.put("/api/v1/records/1", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["no2"] == 35.0
    
    def test_update_nonexistent_record(self, client):
        """Test 404 when updating non-existent record"""
        update_data = {"no2": 35.0}
        response = client.put("/api/v1/records/999", json=update_data)
        assert response.status_code == 404
    
    def test_delete_record(self, client):
        """Test deleting a record"""
        response = client.delete("/api/v1/records/1")
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get("/api/v1/records/1")
        assert response.status_code == 404
    
    def test_delete_nonexistent_record(self, client):
        """Test 404 when deleting non-existent record"""
        response = client.delete("/api/v1/records/999")
        assert response.status_code == 404


# ============== Metadata Tests ==============

class TestMetadataEndpoints:
    """Tests for metadata endpoints"""
    
    def test_get_regions(self, client):
        """Test getting list of regions"""
        response = client.get("/api/v1/regions")
        assert response.status_code == 200
        data = response.json()
        assert "regions" in data
        assert len(data["regions"]) == 3
        assert "Île-de-France" in data["regions"]
    
    def test_get_communes(self, client):
        """Test getting list of communes"""
        response = client.get("/api/v1/communes")
        assert response.status_code == 200
        data = response.json()
        assert "communes" in data
        assert len(data["communes"]) == 3
    
    def test_get_communes_by_region(self, client):
        """Test getting communes filtered by region"""
        response = client.get("/api/v1/communes?region=Île-de-France")
        assert response.status_code == 200
        data = response.json()
        assert len(data["communes"]) == 1
        assert "Paris" in data["communes"]
    
    def test_get_years(self, client):
        """Test getting list of available years"""
        response = client.get("/api/v1/years")
        assert response.status_code == 200
        data = response.json()
        assert "years" in data
        assert 2020 in data["years"]
        assert 2021 in data["years"]


# ============== Statistics Tests ==============

class TestStatisticsEndpoints:
    """Tests for statistics endpoints"""
    
    def test_get_region_stats(self, client):
        """Test getting region statistics"""
        response = client.get("/api/v1/stats/region/Île-de-France")
        assert response.status_code == 200
        data = response.json()
        assert data["region"] == "Île-de-France"
        assert data["count"] == 2
        assert "avg_no2" in data
    
    def test_get_region_stats_with_year(self, client):
        """Test getting region statistics filtered by year"""
        response = client.get("/api/v1/stats/region/Île-de-France?annee=2020")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
    
    def test_get_nonexistent_region_stats(self, client):
        """Test 404 for non-existent region"""
        response = client.get("/api/v1/stats/region/NonExistent")
        assert response.status_code == 404
    
    def test_get_commune_stats(self, client):
        """Test getting commune statistics"""
        response = client.get("/api/v1/stats/commune/Paris")
        assert response.status_code == 200
        data = response.json()
        assert data["commune"] == "Paris"
        assert data["count"] == 2
    
    def test_get_pollutant_trend(self, client):
        """Test getting pollutant trend"""
        response = client.get("/api/v1/trends/no2")
        assert response.status_code == 200
        data = response.json()
        assert data["pollutant"] == "no2"
        assert "data" in data
        assert len(data["data"]) > 0
    
    def test_get_pollutant_trend_with_region(self, client):
        """Test getting pollutant trend filtered by region"""
        response = client.get("/api/v1/trends/no2?region=Île-de-France")
        assert response.status_code == 200
        data = response.json()
        assert data["region"] == "Île-de-France"
    
    def test_get_invalid_pollutant_trend(self, client):
        """Test 400 for invalid pollutant"""
        response = client.get("/api/v1/trends/invalid")
        assert response.status_code == 400
    
    def test_compare_regions(self, client):
        """Test comparing multiple regions"""
        response = client.get("/api/v1/compare?regions=Île-de-France,Provence-Alpes-Côte d'Azur")
        assert response.status_code == 200
        data = response.json()
        assert "comparison" in data
        assert len(data["comparison"]) == 2
    
    def test_compare_single_region_error(self, client):
        """Test error when comparing single region"""
        response = client.get("/api/v1/compare?regions=Île-de-France")
        assert response.status_code == 400
    
    def test_get_summary(self, client):
        """Test getting dataset summary"""
        response = client.get("/api/v1/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 4
        assert data["total_regions"] == 3
        assert "global_averages" in data
        assert "year_range" in data


# ============== Integration Tests ==============

class TestIntegration:
    """Integration tests"""
    
    def test_create_and_retrieve_record(self, client):
        """Test creating and then retrieving a record"""
        new_record = {
            "commune": "Toulouse",
            "code_insee": "31555",
            "region": "Occitanie",
            "departement": "Haute-Garonne",
            "annee": 2022,
            "no2": 24.8,
            "pm10": 18.5
        }
        
        # Create
        create_response = client.post("/api/v1/records", json=new_record)
        assert create_response.status_code == 201
        created_id = create_response.json()["id"]
        
        # Retrieve
        get_response = client.get(f"/api/v1/records/{created_id}")
        assert get_response.status_code == 200
        assert get_response.json()["commune"] == "Toulouse"
    
    def test_update_affects_stats(self, client):
        """Test that updating a record affects statistics"""
        # Get initial stats
        initial_stats = client.get("/api/v1/stats/commune/Paris").json()
        initial_avg = initial_stats["avg_no2"]
        
        # Update a record
        client.put("/api/v1/records/1", json={"no2": 100.0})
        
        # Get updated stats
        updated_stats = client.get("/api/v1/stats/commune/Paris").json()
        updated_avg = updated_stats["avg_no2"]
        
        # Average should have increased
        assert updated_avg > initial_avg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
