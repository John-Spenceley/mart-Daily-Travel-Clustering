
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from helpers.clustering import cluster_itinerary

router = APIRouter(prefix="/optimize", tags=["optimize"])

class POI(BaseModel):
    title: str
    lat: float
    lng: float
    duration_min: int = Field(default=60)
    category: Optional[str] = None

class Hotel(BaseModel):
    name: str
    lat: float
    lng: float

class ClusterRequest(BaseModel):
    pois: List[POI]
    hotel: Optional[Hotel] = None
    radius_km: float = 1.2
    start_time: str = "09:00"
    end_time: str = "19:00"
    transport_mode: str = "walk"

@router.post("/cluster")
def optimize_cluster(req: ClusterRequest) -> Dict[str, Any]:
    if not req.pois:
        raise HTTPException(status_code=400, detail="No POIs provided.")
    try:
        plan = cluster_itinerary(
            pois=[p.model_dump() for p in req.pois],
            hotel=req.hotel.model_dump() if req.hotel else None,
            radius_km=req.radius_km,
            start_time=req.start_time,
            end_time=req.end_time,
            transport_mode=req.transport_mode
        )
        return {"days": plan, "radius_km": req.radius_km}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
