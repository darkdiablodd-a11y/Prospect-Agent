from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .scoring import ScoredProspect


def _record(item: ScoredProspect) -> dict[str, object]:
    public_email = item.website.public_emails[0] if item.website.public_emails else ""
    return {
        "score": item.score,
        "business_name": item.place.name,
        "category": item.place.search_category,
        "address": item.place.address,
        "phone": item.place.phone,
        "website": item.place.website,
        "google_maps": item.place.maps_url,
        "rating": item.place.rating,
        "review_count": item.place.review_count,
        "likely_decision_maker": item.likely_decision_maker,
        "employee_fit_estimate": item.employee_fit_estimate,
        "agency_need": item.agency_need,
        "decision_access": item.decision_access,
        "commercial_fit": item.commercial_fit,
        "local_confidence": item.local_confidence,
        "reasons": "; ".join(item.reasons),
        "meeting_angle": item.meeting_angle,
        "contact_email": public_email,
        "email_source": item.website.final_url if public_email else "",
        "email_verification": "public website match" if public_email else "not found",
        "outreach_status": "awaiting approval" if public_email else "email research needed",
        "send_eligible": False,
    }


def write_reports(items: list[ScoredProspect], output_dir: str | Path) -> None:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    records = [_record(item) for item in items]
    fields = list(records[0]) if records else [
        "score", "business_name", "category", "address", "phone", "website",
        "google_maps", "rating", "review_count", "likely_decision_maker",
        "employee_fit_estimate",
        "agency_need", "decision_access", "commercial_fit", "local_confidence",
        "reasons", "meeting_angle",
        "contact_email", "email_source", "email_verification",
        "outreach_status", "send_eligible",
    ]
    with (target / "prospects.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    (target / "prospects.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    outreach_fields = [
        "business_name", "contact_email", "email_source", "email_verification",
        "outreach_status", "send_eligible", "meeting_angle",
    ]
    with (target / "outreach_queue.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=outreach_fields)
        writer.writeheader()
        writer.writerows(
            {field: record[field] for field in outreach_fields}
            for record in records
        )
    lines = ["# Prospect Briefing", "", f"Qualified prospects: **{len(items)}**", ""]
    for index, item in enumerate(items[:25], 1):
        p = item.place
        lines.extend(
            [
                f"## {index}. {p.name} — {item.score}/100",
                "",
                f"- **Category:** {p.search_category}",
                f"- **Location:** {p.address}",
                f"- **Contact:** {p.phone or 'No public phone'} · {p.website or 'No website'}",
                f"- **Ask for:** {item.likely_decision_maker}",
                f"- **Size fit:** {item.employee_fit_estimate}",
                f"- **Why now:** {'; '.join(item.reasons[:4])}",
                f"- **Meeting angle:** {item.meeting_angle}",
                "",
            ]
        )
    (target / "briefing.md").write_text("\n".join(lines), encoding="utf-8")
