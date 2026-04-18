from pydantic import BaseModel, Field, field_validator


class RouteOptimizeRequest(BaseModel):
    locations: list[list[float]] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="A list of [latitude, longitude] coordinates.",
    )

    @field_validator("locations")
    @classmethod
    def validate_locations(cls, value: list[list[float]]) -> list[list[float]]:
        for index, coordinate in enumerate(value):
            if len(coordinate) != 2:
                raise ValueError(f"Location at index {index} must contain exactly [lat, lon].")

            lat, lon = coordinate
            if not (-90 <= lat <= 90):
                raise ValueError(f"Latitude at index {index} must be between -90 and 90.")
            if not (-180 <= lon <= 180):
                raise ValueError(f"Longitude at index {index} must be between -180 and 180.")

        return value


class RouteOptimizeResponse(BaseModel):
    optimal_route: list[list[float]]
    total_distance_km: float
