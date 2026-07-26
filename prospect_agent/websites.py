from __future__ import annotations

import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field


@dataclass
class WebsiteSignals:
    reachable: bool = False
    final_url: str = ""
    text: str = ""
    has_contact: bool = False
    has_booking: bool = False
    has_about_or_team: bool = False
    has_owner_language: bool = False
    has_social_links: bool = False
    has_analytics: bool = False
    has_https: bool = False
    has_chat: bool = False
    has_careers: bool = False
    has_multiple_locations: bool = False
    has_inquiry_language: bool = False
    errors: list[str] = field(default_factory=list)


def inspect_website(url: str, timeout: int, user_agent: str) -> WebsiteSignals:
    if not url:
        return WebsiteSignals(errors=["No website listed"])
    try:
        request = urllib.request.Request(url, headers={"User-Agent": user_agent})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(750_000).decode("utf-8", errors="ignore")
            final_url = response.geturl()
    except (urllib.error.URLError, ValueError, TimeoutError) as exc:
        return WebsiteSignals(errors=[f"Website unavailable: {type(exc).__name__}"])

    lower = raw.lower()
    visible = re.sub(r"<script\b[^>]*>.*?</script>", " ", lower, flags=re.S)
    visible = re.sub(r"<style\b[^>]*>.*?</style>", " ", visible, flags=re.S)
    visible = re.sub(r"<[^>]+>", " ", visible)
    visible = re.sub(r"\s+", " ", visible)[:100_000]
    return WebsiteSignals(
        reachable=True,
        final_url=final_url,
        text=visible,
        has_contact=any(x in lower for x in ["/contact", "contact us", "get in touch"]),
        has_booking=any(
            x in lower
            for x in ["book now", "schedule online", "request appointment", "book online"]
        ),
        has_about_or_team=any(
            x in lower for x in ["/about", "/team", "meet the team", "our team"]
        ),
        has_owner_language=any(
            x in visible
            for x in ["owner", "founder", "family-owned", "locally owned", "principal"]
        ),
        has_social_links=any(
            x in lower
            for x in ["facebook.com/", "instagram.com/", "linkedin.com/company/"]
        ),
        has_analytics=any(
            x in lower for x in ["googletagmanager.com", "google-analytics.com", "gtag("]
        ),
        has_https=urllib.parse.urlparse(final_url).scheme == "https",
        has_chat=any(
            x in lower
            for x in ["intercom", "drift.com", "crisp.chat", "livechat", "zendesk"]
        ),
        has_careers=any(x in lower for x in ["/careers", "/jobs", "join our team"]),
        has_multiple_locations=any(
            x in visible
            for x in ["our locations", "multiple locations", "locations near you"]
        ),
        has_inquiry_language=any(
            x in visible
            for x in [
                "request a quote", "free estimate", "request an appointment",
                "schedule a consultation", "call today", "contact us today",
            ]
        ),
    )
