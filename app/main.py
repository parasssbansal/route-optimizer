from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.optimize import route_optimizer, router as optimize_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await route_optimizer.osrm_service.close()


app = FastAPI(
    title="Route Optimizer API",
    version="1.0.0",
    description="Optimize delivery or travel stops using OSRM distance data and TSP.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(optimize_router)
