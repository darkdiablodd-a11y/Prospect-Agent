from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .config import load_config
from .places import PlacesClient
from .reporting import write_reports
from .scoring import score
from .websites import inspect_website


def main() -> int:
    parser = argparse.ArgumentParser(description="Find and rank Charlotte-area prospects.")
    parser.add_argument("--config", default="config/agency.yaml")
    parser.add_argument("--output", default="output")
    parser.add_argument("--limit-searches", type=int, default=0)
    args = parser.parse_args()

    config = load_config(args.config)
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY", "").strip()
    if not api_key:
        print("Missing GOOGLE_PLACES_API_KEY.", file=sys.stderr)
        return 2

    searches = [(c, l) for l in config.locations for c in config.categories]
    if args.limit_searches:
        searches = searches[: args.limit_searches]
    client = PlacesClient(api_key)
    unique = {}
    for number, (category, location) in enumerate(searches, 1):
        print(f"[{number}/{len(searches)}] {category} — {location}")
        for place in client.search(category, location, config.results_per_search):
            unique.setdefault(place.place_id, place)

    inspection_queue = sorted(
        unique.values(),
        key=lambda place: (
            bool(place.phone),
            bool(place.website),
            place.business_status == "OPERATIONAL",
            min(place.review_count, 500),
            place.rating,
        ),
        reverse=True,
    )[: config.maximum_website_inspections]

    ranked = []
    for number, place in enumerate(inspection_queue, 1):
        print(f"Inspecting website {number}/{len(inspection_queue)}: {place.name}")
        signals = inspect_website(
            place.website, config.website_timeout_seconds, config.user_agent
        )
        ranked.append(score(place, signals, config.offer))

    qualified = sorted(
        (
            item
            for item in ranked
            if item.score >= config.minimum_score
            and item.decision_access >= config.minimum_decision_access
        ),
        key=lambda item: (item.score, item.place.review_count),
        reverse=True,
    )[: config.maximum_results]
    write_reports(qualified, args.output)
    print(f"Wrote {len(qualified)} qualified prospects to {Path(args.output).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
