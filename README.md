# Prospect by Nightshift Labs

A GitHub Actions-ready prospecting agent from **Nightshift Labs**, targeting inquiry-heavy
local businesses in Charlotte, North Carolina and surrounding communities for
Agentic AI automation.

It:

- discovers local businesses with Google Places Text Search;
- checks public business websites for marketing and accessibility signals;
- scores agency fit, ability to reach a decision maker, and likely budget;
- prioritizes businesses showing demand for calls, quotes, consultations, or
  appointments where AI can improve intake and follow-up;
- excludes chains and businesses without a usable public contact path;
- writes a ranked CSV, JSON, and human-readable briefing;
- creates an approval-first outreach queue using public business emails found
  on the companies' own websites;
- can run manually or every Monday in GitHub Actions.

The tool does **not** guess personal emails, bypass access controls, or send
messages. Sending stays locked until Nightshift Labs deliberately adds and
configures a provider. It records public business contact paths and recommends
the likely role to ask for (owner, practice manager, general manager, etc.).

## Quick start

1. Create a Google Cloud project, enable **Places API (New)**, and create an API
   key.
2. Copy `.env.example` to `.env` and add the key, or export
   `GOOGLE_PLACES_API_KEY`.
3. Edit `config/agency.yaml` to describe your offer and ideal clients.
4. Run:

```bash
python3 -m prospect_agent --config config/agency.yaml
```

Results appear in `output/`:

- `prospects.csv` — CRM-friendly ranked list
- `prospects.json` — complete structured output
- `briefing.md` — the best leads and suggested meeting angles
- `outreach_queue.csv` — email research and approval status; never an automatic send list

No third-party Python packages are required.

## GitHub deployment

Push this directory to a GitHub repository, then add an Actions repository
secret named `GOOGLE_PLACES_API_KEY`. The workflow in
`.github/workflows/prospect-agent.yml` can be launched from the **Actions** tab
and runs automatically on the 1st and 15th of each month at 13:00 UTC
(approximately 9:00 AM Eastern during daylight-saving time and 8:00 AM Eastern
otherwise).

Each run uploads the reports as a downloadable artifact. To keep a historical
record in the repository, run locally and commit the output intentionally; the
scheduled workflow does not push changes.

## Configuration

`config/agency.yaml` uses a deliberately small YAML subset so the project stays
dependency-free. Change:

- `offer` and `outcomes` to match what your agency sells;
- `categories` to the niches you serve best;
- `locations` to expand or narrow the territory;
- `target_employee_min` and `target_employee_max` to document the desired size;
- `minimum_score`, `minimum_decision_access`, and `maximum_results` to control
  the shortlist. The accessibility floor prevents a high-need business with no
  practical public contact route from crowding out meeting-ready leads.
- `maximum_website_inspections` limits slower website analysis to the strongest
  candidates identified from the complete Places search.

Search volume affects Google Places usage and cost. Start with a few categories
and locations, review the output, and expand deliberately.

## How scoring works

The 100-point score balances:

- **Agency need (40):** weak/outdated web presence, missing calls to action,
  limited online booking, and other visible growth gaps.
- **Decision-maker access (30):** public phone/contact path, local/operator-led
  language, team/about pages, and a business type where a manager or owner is
  normally reachable.
- **Commercial fit (20):** review volume, rating, active operating status, and
  business categories commonly able to invest in growth.
- **Local confidence (10):** Charlotte-area address and non-chain signals.

A high score is a research priority, not a claim that the business needs a
particular service. Review the evidence and personalize any outreach.

Google Places does not report employee counts. The agent therefore labels size
fit as an estimate based on public scale signals such as review volume, team and
careers content, and multiple locations. Verify the 10–100 employee criterion
with the company website, LinkedIn, or a reputable business-data provider before
adding a prospect to an outreach sequence.

## Safety and compliance

Use the output for one-to-one, relevant business development. Honor opt-outs,
applicable telemarketing/email laws, platform terms, and your CRM suppression
list. Do not infer sensitive traits or collect personal contact details that the
business has not intentionally published for business use.

## Tests

```bash
python3 -m unittest discover -s tests -v
```
