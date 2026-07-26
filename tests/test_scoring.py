import unittest
from unittest.mock import patch

from prospect_agent.places import Place
from prospect_agent.scoring import score
from prospect_agent.websites import WebsiteSignals
from prospect_agent.websites import inspect_website


class ScoringTests(unittest.TestCase):
    def test_owner_led_business_with_growth_gap_scores_well(self):
        place = Place(
            "abc", "Queen City Family Dentistry", "Charlotte, NC", "704-555-0100",
            "https://example.com", "https://maps.example/abc", 4.7, 84, "dentist",
            "OPERATIONAL", "dentist", "Charlotte, NC"
        )
        site = WebsiteSignals(
            reachable=True, has_contact=True, has_about_or_team=True,
            has_owner_language=True, has_https=True
        )
        result = score(place, site, "websites and lead generation")
        self.assertGreaterEqual(result.score, 55)
        self.assertIn("practice manager", result.likely_decision_maker)
        self.assertIn("employee", result.employee_fit_estimate.lower())

    def test_missing_website_creates_need_but_not_fake_contact_access(self):
        place = Place(
            "xyz", "Local Landscapes", "Matthews, NC", "", "", "", 4.4, 35,
            "landscaper", "OPERATIONAL", "landscaping company", "Matthews, NC"
        )
        result = score(place, WebsiteSignals(), "local SEO")
        self.assertEqual(result.agency_need, 25)
        self.assertEqual(result.decision_access, 0)

    @patch("prospect_agent.websites.urllib.request.urlopen")
    def test_disconnected_website_is_recorded_not_fatal(self, mock_urlopen):
        import http.client

        mock_urlopen.side_effect = http.client.RemoteDisconnected("closed")
        result = inspect_website("https://example.com", 1, "test-agent")
        self.assertFalse(result.reachable)
        self.assertTrue(result.errors)


if __name__ == "__main__":
    unittest.main()
