from __future__ import annotations

import re
from dataclasses import dataclass

from .places import Place
from .websites import WebsiteSignals


CHAIN_MARKERS = {
    "walmart",
    "target",
    "mcdonald",
    "starbucks",
    "home depot",
    "lowe's",
    "cvs",
    "walgreens",
    "aspens dental",
    "great clips",
}
HIGH_VALUE_TYPES = {
    "dentist",
    "doctor",
    "lawyer",
    "veterinary_care",
    "roofing_contractor",
    "plumber",
    "electrician",
    "general_contractor",
    "spa",
    "physiotherapist",
}
ROLE_BY_CATEGORY = {
    "dentist": "Owner dentist or practice manager",
    "med spa": "Owner, medical director, or practice manager",
    "chiropractor": "Owner chiropractor or office manager",
    "physical therapy clinic": "Clinic director or owner",
    "family law firm": "Managing partner or firm administrator",
    "estate planning attorney": "Managing partner or owner attorney",
    "veterinarian": "Practice owner or hospital manager",
    "boutique fitness studio": "Studio owner or general manager",
    "auto repair shop": "Owner or general manager",
}


@dataclass
class ScoredProspect:
    place: Place
    website: WebsiteSignals
    score: int
    agency_need: int
    decision_access: int
    commercial_fit: int
    local_confidence: int
    likely_decision_maker: str
    employee_fit_estimate: str
    reasons: list[str]
    meeting_angle: str


def _is_chain(name: str) -> bool:
    normalized = re.sub(r"[^a-z0-9' ]", "", name.lower())
    return any(marker in normalized for marker in CHAIN_MARKERS)


def _role(category: str) -> str:
    if category in ROLE_BY_CATEGORY:
        return ROLE_BY_CATEGORY[category]
    if any(x in category for x in ["contractor", "plumber", "electrician", "landscap"]):
        return "Owner or general manager"
    return "Owner, founder, or general manager"


def score(place: Place, site: WebsiteSignals, offer: str) -> ScoredProspect:
    need, access, commercial, local = 0, 0, 0, 0
    reasons: list[str] = []

    if not place.website:
        need += 25
        reasons.append("No website is listed")
    elif not site.reachable:
        need += 22
        reasons.append("Listed website was not reachable")
    else:
        if not site.has_booking:
            need += 7
            reasons.append("No obvious automated booking or appointment path")
        if not site.has_contact:
            need += 5
            reasons.append("No obvious contact call-to-action")
        if not site.has_chat:
            need += 7
            reasons.append("No common live-chat or conversational intake tool detected")
        if not site.has_analytics:
            need += 3
        if not site.has_social_links:
            need += 2
        if not site.has_https:
            need += 8
            reasons.append("Website did not resolve to HTTPS")
    need = min(need, 40)

    if place.phone:
        access += 13
        reasons.append("Public business phone is available")
    if site.has_contact:
        access += 6
    if site.has_about_or_team:
        access += 5
        reasons.append("Team/about content can support personalization")
    if site.has_owner_language:
        access += 6
        reasons.append("Owner/founder language suggests local leadership access")
    if place.search_category in ROLE_BY_CATEGORY:
        access += 4
    access = min(access, 30)

    if place.business_status == "OPERATIONAL":
        commercial += 3
    if place.rating >= 4.2:
        commercial += 4
    if 20 <= place.review_count <= 500:
        commercial += 7
        reasons.append("Established locally without obvious enterprise scale")
    elif place.review_count > 500:
        commercial += 5
    elif place.review_count >= 5:
        commercial += 3
    if place.primary_type in HIGH_VALUE_TYPES:
        commercial += 6
    if site.has_inquiry_language:
        commercial += 4
        reasons.append("Website actively solicits quotes, calls, or consultations")
    commercial = min(commercial, 20)

    if any(x in place.address.lower() for x in ["nc", "sc"]):
        local += 4
    chain = _is_chain(place.name)
    if not chain:
        local += 6
    else:
        reasons.append("Possible chain; manual ownership check recommended")
    local = min(local, 10)

    total = need + access + commercial + local
    size_signals = sum(
        [
            place.review_count >= 40,
            site.has_about_or_team,
            site.has_careers,
            site.has_multiple_locations,
        ]
    )
    if size_signals >= 3:
        employee_fit = "Strong 10–100 employee proxy; verify before outreach"
    elif size_signals == 2:
        employee_fit = "Possible 10–100 employee fit; verify before outreach"
    else:
        employee_fit = "Employee count unknown; limited public size signals"
    angle = (
        f"Lead with a specific observation about {reasons[0].lower() if reasons else 'their local presence'}; "
        "ask how inquiries are handled after hours and during busy periods, then "
        f"connect the gap to {offer.lower()} and request a 15-minute workflow review."
    )
    return ScoredProspect(
        place=place,
        website=site,
        score=total,
        agency_need=need,
        decision_access=access,
        commercial_fit=commercial,
        local_confidence=local,
        likely_decision_maker=_role(place.search_category),
        employee_fit_estimate=employee_fit,
        reasons=reasons,
        meeting_angle=angle,
    )
