import httpx
import json
import logging
import pytest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_api():
    with httpx.Client(timeout=30.0) as client:
        # 1. Test Municipality
        logger.info("Testing /locations/municipalities/1685...")
        r = client.get(f"{BASE_URL}/locations/municipalities/1685")
        assert r.status_code == 200
        data = r.json()
        assert "name" in data
        assert "code" in data
        assert "province_name" in data
        print(f"Municipality: {data['name']} ({data['code']})")

        # 2. Test Search
        logger.info("Testing /locations/search...")
        r = client.post(f"{BASE_URL}/locations/search", json={"query": "Milano"})
        assert r.status_code == 200
        data = r.json()
        assert data["found"] is True
        assert data["municipality"] is not None
        print(f"Search 'Milano' found: {data['municipality']['name']}")

        # 3. Test Score
        logger.info("Testing /scores/municipality/1685...")
        r = client.get(f"{BASE_URL}/scores/municipality/1685")
        assert r.status_code == 200
        data = r.json()
        assert "overall_score" in data
        assert "recommendation" in data
        assert "strengths" in data
        assert "component_scores" in data
        print(f"Investment Score: {data['overall_score']} - {data['score_category']}")
        print(f"Recommendation: {data['recommendation']}")

        # 4. Test Risk
        logger.info("Testing /risks/municipality/1685...")
        r = client.get(f"{BASE_URL}/risks/municipality/1685")
        assert r.status_code == 200
        data = r.json()
        assert "overall_risk_level" in data
        assert "seismic_risk" in data
        assert "flood_risk" in data
        assert "landslide_risk" in data
        # Check if climate projection is present or None (depends on data)
        print(f"Risk Assessment: {data['overall_risk_level']} (Score: {data['total_risk_score']})")

        # 5. Test Property Prices
        logger.info("Testing /properties/prices/municipality/1685...")
        r = client.get(f"{BASE_URL}/properties/prices/municipality/1685")
        assert r.status_code == 200
        data = r.json()
        if data:
            assert "avg_price" in data[0]
            assert "year" in data[0]
            print(f"Sample Price: {data[0]['avg_price']} €/sqm in {data[0]['year']}")
        else:
            print("No property prices found for this municipality")

if __name__ == "__main__":
    test_api()
