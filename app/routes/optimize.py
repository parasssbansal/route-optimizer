from fastapi import APIRouter, HTTPException, status

from app.models.route import RouteOptimizeRequest, RouteOptimizeResponse
from app.services.route_optimizer import RouteOptimizerService

router = APIRouter(tags=["routing"])
route_optimizer = RouteOptimizerService()


@router.post(
    "/optimize-route",
    response_model=RouteOptimizeResponse,
    status_code=status.HTTP_200_OK,
)
async def optimize_route(payload: RouteOptimizeRequest) -> RouteOptimizeResponse:
    try:
        result = await route_optimizer.optimize(payload.locations)
        return RouteOptimizeResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
