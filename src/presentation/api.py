from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from application.factory import create_recommendation_service
from application.preference_validator import PreferenceValidationError, PreferenceValidator
from domain.models.preferences import UserBudget, UserPreferences
from domain.models.recommendation import RecommendationBatch
from infrastructure.config import get_settings

recommendation_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global recommendation_service
    settings = get_settings()
    recommendation_service = create_recommendation_service(settings)
    yield

app = FastAPI(title="Zomato Restaurant Recommender API", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PreferenceRequest(BaseModel):
    location: str
    budget: str
    cuisine: str
    min_rating: float = Field(default=3.5, ge=0.0, le=5.0)
    additional_preferences: str | None = None

@app.get("/health")
def health():
    if recommendation_service is None:
        return {"status": "starting"}
    repo = recommendation_service._candidate_filter._repository
    return {
        "status": "healthy",
        "restaurant_count": repo.count()
    }

@app.get("/api/locations")
def get_locations():
    if recommendation_service is None:
        raise HTTPException(status_code=503, detail="Service initializing")
    repo = recommendation_service._candidate_filter._repository
    restaurants = repo.find_all()
    areas = set(r.area for r in restaurants if r.area)
    cities = set(r.location for r in restaurants if r.location)
    locations = sorted(list(cities | areas))
    return {"locations": locations}

@app.post("/api/recommend", response_model=RecommendationBatch)
def recommend(request: PreferenceRequest):
    import sys
    print(f"--- API RECOMMEND REQUEST: {request.model_dump()}", file=sys.stderr)
    if recommendation_service is None:
        raise HTTPException(status_code=503, detail="Service initializing")
    
    try:
        prefs = PreferenceValidator().validate({
            "location": request.location,
            "budget": request.budget,
            "cuisine": request.cuisine,
            "min_rating": request.min_rating,
            "additional_preferences": request.additional_preferences,
        })
    except PreferenceValidationError as exc:
        raise HTTPException(status_code=400, detail="; ".join(exc.messages))
        
    try:
        batch = recommendation_service.recommend(prefs)
        print(f"--- API RECOMMEND RESPONSE count: {len(batch.recommendations)}", file=sys.stderr)
        return batch
    except Exception as exc:
        print(f"--- API RECOMMEND ERROR: {exc}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(exc))
