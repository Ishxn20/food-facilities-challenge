import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_json(endpoint, params=None):
    response = client.get(endpoint, params=params)
    return response

def test_search_applicant_missing_name():
    r = get_json("/search/applicant", params={})
    assert r.status_code == 422

def test_search_applicant_empty_name():
    r = get_json("/search/applicant", params={"name": ""})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_search_applicant_nonexistent():
    r = get_json("/search/applicant", params={"name": "___NOTFOUND___"})
    assert r.status_code == 200
    assert r.json() == []

def test_search_applicant_basic():
    r = get_json("/search/applicant", params={"name": "Geez Freeze"})
    assert r.status_code == 200
    data = r.json()
    assert any("Geez Freeze" in f["Applicant"] for f in data)

def test_search_applicant_status_filter_case_insensitive():
    r1 = get_json("/search/applicant", params={"name": "Geez", "status": "approved"})
    r2 = get_json("/search/applicant", params={"name": "Geez", "status": "APPROVED"})
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json() == r2.json()
    for f in r1.json():
        assert f["Status"].upper() == "APPROVED"

def test_search_applicant_invalid_status():
    r = get_json("/search/applicant", params={"name": "Geez", "status": "INVALID"})
    assert r.status_code == 200
    assert r.json() == []

def test_search_address_missing_street():
    r = get_json("/search/address", params={})
    assert r.status_code == 422

def test_search_address_empty_street():
    r = get_json("/search/address", params={"street": ""})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_search_address_nonexistent():
    r = get_json("/search/address", params={"street": "___NOTFOUND___"})
    assert r.status_code == 200
    assert r.json() == []

def test_search_address_partial_case_insensitive():
    r = get_json("/search/address", params={"street": "san"})
    assert r.status_code == 200
    data = r.json()
    assert all("SAN" in f["Address"].upper() for f in data)

def test_search_address_status_filter():
    r = get_json("/search/address", params={"street": "MILK", "status": "REQUESTED"})
    assert r.status_code == 200
    for f in r.json():
        assert f["Status"].upper() == "REQUESTED"

def test_search_nearby_missing_params():
    r1 = get_json("/search/nearby", params={"lon": 0})
    r2 = get_json("/search/nearby", params={"lat": 0})
    assert r1.status_code == 422
    assert r2.status_code == 422

def test_search_nearby_invalid_lat_lon():
    response = client.get("/search/nearby", params={"lat": 1000, "lon": 0, "limit": 1})
    assert response.status_code == 400
    assert "Latitude" in response.json()["detail"]

def test_search_nearby_limit_zero_and_negative():
    for limit in [0, -1]:
        r = get_json("/search/nearby", params={"lat": 37.762, "lon": -122.427, "limit": limit})
        assert r.status_code == 200
        assert r.json() == []

def test_search_nearby_limit_one():
    r = get_json("/search/nearby", params={"lat": 37.762, "lon": -122.427, "limit": 1})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1

def test_search_nearby_default_limit_and_status():
    r = get_json("/search/nearby", params={"lat": 37.762, "lon": -122.427})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 5
    for entry, dist in data:
        assert entry["Status"].upper() == "APPROVED"
        assert isinstance(dist, (int, float))

def test_search_nearby_include_all_flag_behavior():
    params = {"lat": 37.762, "lon": -122.427, "limit": 10}
    r_default = get_json("/search/nearby", params=params)
    params_all = params.copy()
    params_all["include_all"] = True
    r_all = get_json("/search/nearby", params=params_all)
    assert r_default.status_code == 200 and r_all.status_code == 200
    assert len(r_all.json()) >= len(r_default.json())

def test_applicant_response_schema():
    r = get_json("/search/applicant", params={"name": ""})
    data = r.json()
    if data:
        keys = set(data[0].keys())
        expected = {"locationid", "Applicant", "Address", "Status", "Latitude", "Longitude"}
        assert expected.issubset(keys)

def test_address_response_schema():
    r = get_json("/search/address", params={"street": ""})
    data = r.json()
    if data:
        keys = set(data[0].keys())
        expected = {"locationid", "Applicant", "Address", "Status", "Latitude", "Longitude"}
        assert expected.issubset(keys)