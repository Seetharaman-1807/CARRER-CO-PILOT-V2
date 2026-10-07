from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.profile import router as profile_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.analyses import router as analyses_router
from app.api.v1.skills import router as skills_router
from app.api.v1.roadmap import router as roadmap_router
from app.api.v1.dsa import router as dsa_router
from app.api.v1.interviews import router as interviews_router
from app.api.v1.dashboard import router as dashboard_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(resumes_router)
api_router.include_router(jobs_router)
api_router.include_router(analyses_router)
api_router.include_router(skills_router)
api_router.include_router(roadmap_router)
api_router.include_router(dsa_router)
api_router.include_router(interviews_router)
api_router.include_router(dashboard_router)
