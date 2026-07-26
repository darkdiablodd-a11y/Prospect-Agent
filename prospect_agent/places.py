from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


ENDPOINT = "https://places.googleapis.com/v1/places:searchText"
FIELDS = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.nationalPhoneNumber",
        "places.websiteUri",
        "places.googleMapsUri",
        "places.rating",
        "places.userRatingCount",
        "places.primaryType",
        "places.businessStatus",
    ]
)


@dataclass
class Place:
    place_id: str
    name: str
    address: str
    phone: str
    website: str
    maps_url: str
    rating: float
    review_count: int
    primary_type: str
    business_status: str
    search_category: str
    search_location: str


class PlacesClient:
    def __init__(self, api_key: str, timeout: int = 20) -> None:
        self.api_key = api_key
        self.timeout = timeout

    def search(self, category: str, location: str, page_size: int) -> list[Place]:
        body = json.dumps(
            {
                "textQuery": f"{category} in {location}",
                "pageSize": min(max(page_size, 1), 20),
                "languageCode": "en",
                "regionCode": "US",
            }
        ).encode()
        request = urllib.request.Request(
            ENDPOINT,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": FIELDS,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload: dict[str, Any] = json.load(response)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Places API returned {exc.code}: {detail}") from exc
        return [
            Place(
                place_id=item.get("id", ""),
                name=item.get("displayName", {}).get("text", ""),
                address=item.get("formattedAddress", ""),
                phone=item.get("nationalPhoneNumber", ""),
                website=item.get("websiteUri", ""),
                maps_url=item.get("googleMapsUri", ""),
                rating=float(item.get("rating", 0)),
                review_count=int(item.get("userRatingCount", 0)),
                primary_type=item.get("primaryType", ""),
                business_status=item.get("businessStatus", ""),
                search_category=category,
                search_location=location,
            )
            for item in payload.get("places", [])
        ]

    def search_all(
        self, categories: list[str], locations: list[str], page_size: int
    ) -> list[Place]:
        found: dict[str, Place] = {}
        for location in locations:
            for category in categories:
                for place in self.search(category, location, page_size):
                    if place.place_id and place.place_id not in found:
                        found[place.place_id] = place
                time.sleep(0.05)
        return list(found.values())

