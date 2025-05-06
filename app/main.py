from fastapi import FastAPI, Query, HTTPException
from starlette.responses import RedirectResponse
from pydantic import BaseModel
import pandas as pd
from haversine import haversine, Unit
from typing import List, Optional, Tuple
from fastapi.responses import HTMLResponse

app = FastAPI(title="SF Mobile Food Facilities API")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui")

df = pd.read_csv("Mobile_Food_Facility_Permit.csv")
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

class Facility(BaseModel):
    locationid: int
    Applicant: str
    Address: str
    Status: str
    Latitude: float
    Longitude: float

@app.get("/search/applicant", response_model=List[Facility])
def search_applicant(
    name: str = Query(..., description="Full or partial applicant name"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    q = df[df["Applicant"].str.contains(name, case=False, na=False)]
    if status:
        q = q[q["Status"].str.casefold() == status.casefold()]
    return q[["locationid", "Applicant", "Address", "Status", "Latitude", "Longitude"]].to_dict(orient="records")

@app.get("/search/address", response_model=List[Facility])
def search_address(
    street: str = Query(..., description="Substring to match in address"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    q = df[df["Address"].str.contains(street, case=False, na=False)]
    if status:
        q = q[q["Status"].str.casefold() == status.casefold()]
    return q[["locationid", "Applicant", "Address", "Status", "Latitude", "Longitude"]].to_dict(orient="records")

@app.get("/search/nearby", response_model=List[Tuple[Facility, float]])
def search_nearby(
    lat: float = Query(...),
    lon: float = Query(...),
    limit: int = Query(5),
    include_all: bool = Query(False, description="Include all statuses if true")
):
    if lat < -90 or lat > 90:
        raise HTTPException(status_code=400, detail=f"Latitude {lat} out of range [-90, 90]")
    if lon < -180 or lon > 180:
        raise HTTPException(status_code=400, detail=f"Longitude {lon} out of range [-180, 180]")
    subset = df if include_all else df[df["Status"] == "APPROVED"]
    subset = subset.dropna(subset=["Latitude", "Longitude"])
    locs = list(zip(subset["Latitude"], subset["Longitude"]))
    subset = subset.copy()
    subset["distance"] = [haversine((lat, lon), loc, unit=Unit.METERS) for loc in locs]
    nearest = subset.nsmallest(limit, "distance")
    results = []
    for _, row in nearest.iterrows():
        fac = Facility(
            locationid=int(row.locationid),
            Applicant=row.Applicant,
            Address=row.Address,
            Status=row.Status,
            Latitude=row.Latitude,
            Longitude=row.Longitude
        )
        results.append((fac, row.distance))
    return results

@app.get("/ui", include_in_schema=False, response_class=HTMLResponse)
def ui():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8"/>
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"/>
      <title>SF Mobile Food Facilities UI</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"/>
      <style>
        :root {
          --brand-primary: ##020a1e;
          --brand-secondary: #43d3fb;
          --brand-light: #020a1e;
          --brand-dark: #020a1e;
        }
        body { background-color: var(--brand-light); }
        .navbar { background-color: var(--brand-dark) !important; }
        .card {
          border: 2px solid var(--brand-secondary);
          border-radius: 1rem;
          width: 30rem;
        }
        .btn-primary {
          background-color: var(--brand-secondary);
          border-color: var(--brand-secondary);
          color: white;
          opacity: 1 !important;
          visibility: visible !important;
          display: inline-block !important;
        }
        .btn-primary:hover { background-color: var(--brand-secondary); border-color: var(--brand-secondary); }

        /* Make main title white */
        h1.text-center {
          color: #ffffff !important;
        }
      </style>
    </head>
    <body>
      <div class="container py-5">
        <h1 class="text-center mb-5">SF Mobile Food Facilities</h1>
        <div class="row g-4 align-items-stretch">
          <div class="col-md-4 d-flex">
            <div class="card h-100 shadow-sm p-4 bg-white">
              <h5 class="text-dark">Search by Applicant</h5>
              <input id="applicantName" class="form-control my-2" placeholder="Applicant name"/>
              <input id="applicantStatus" class="form-control my-2" placeholder="Status (optional)"/>
              <button onclick="searchApplicant()" class="btn btn-primary w-100 mt-2">Search</button>
              <pre id="applicantResult" class="mt-3 bg-light p-3 rounded" style="height:300px; overflow:auto;"></pre>
            </div>
          </div>
          <div class="col-md-4 d-flex">
            <div class="card h-100 shadow-sm p-4 bg-white">
              <h5 class="text-dark">Search by Address</h5>
              <input id="addressStreet" class="form-control my-2" placeholder="Street substring"/>
              <input id="addressStatus" class="form-control my-2" placeholder="Status (optional)"/>
              <button onclick="searchAddress()" class="btn btn-primary w-100 mt-2">Search</button>
              <pre id="addressResult" class="mt-3 bg-light p-3 rounded" style="height:300px; overflow:auto;"></pre>
            </div>
          </div>
          <div class="col-md-4 d-flex">
            <div class="card h-100 shadow-sm p-4 bg-white">
              <h5 class="text-dark">Nearby Search</h5>
              <input id="lat" class="form-control my-2" placeholder="Latitude"/>
              <input id="lon" class="form-control my-2" placeholder="Longitude"/>
              <input id="limit" type="number" class="form-control my-2" placeholder="Limit" value="5"/>
              <div class="form-check my-2">
                <input type="checkbox" id="includeAll" class="form-check-input"/>
                <label for="includeAll" class="form-check-label text-dark">Include all statuses</label>
              </div>
              <button onclick="searchNearby()" class="btn btn-primary w-100 mt-2">Search</button>
              <pre id="nearbyResult" class="mt-3 bg-light p-3 rounded" style="height:200px; overflow:auto;"></pre>
            </div>
          </div>
        </div>
      </div>
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
      <script>
        async function searchApplicant() {
          const name = document.getElementById("applicantName").value;
          const status = document.getElementById("applicantStatus").value;
          let url = `/search/applicant?name=${encodeURIComponent(name)}`;
          if (status) url += `&status=${encodeURIComponent(status)}`;
          const r = await fetch(url);
          document.getElementById("applicantResult").textContent = JSON.stringify(await r.json(), null, 2);
        }
        async function searchAddress() {
          const street = document.getElementById("addressStreet").value;
          const status = document.getElementById("addressStatus").value;
          let url = `/search/address?street=${encodeURIComponent(street)}`;
          if (status) url += `&status=${encodeURIComponent(status)}`;
          const r = await fetch(url);
          document.getElementById("addressResult").textContent = JSON.stringify(await r.json(), null, 2);
        }
        async function searchNearby() {
          const lat = document.getElementById("lat").value;
          const lon = document.getElementById("lon").value;
          const limit = document.getElementById("limit").value;
          const includeAll = document.getElementById("includeAll").checked;
          const url = `/search/nearby?lat=${lat}&lon=${lon}&limit=${limit}&include_all=${includeAll}`;
          const r = await fetch(url);
          document.getElementById("nearbyResult").textContent = JSON.stringify(await r.json(), null, 2);
        }
      </script>
    </body>
    </html>
    """)