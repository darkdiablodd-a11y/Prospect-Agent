from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    agency_name: str
    offer: str
    outcomes: str
    locations: list[str]
    categories: list[str]
    target_employee_min: int = 10
    target_employee_max: int = 100
    minimum_score: int = 55
    minimum_decision_access: int = 13
    maximum_results: int = 75
    results_per_search: int = 12
    website_timeout_seconds: int = 8
    user_agent: str = "QueenCityProspectAgent/1.0"


def load_config(path: str | Path) -> Config:
    """Load the simple scalar/list YAML used by this project."""
    values: dict[str, object] = {}
    current_list: str | None = None
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            if current_list is None:
                raise ValueError(f"List item without key: {raw}")
            cast_list = values.setdefault(current_list, [])
            assert isinstance(cast_list, list)
            cast_list.append(line[2:].strip())
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"Invalid configuration line: {raw}")
        key, value = key.strip(), value.strip()
        if not value:
            values[key] = []
            current_list = key
        else:
            current_list = None
            values[key] = int(value) if value.isdigit() else value
    return Config(**values)  # type: ignore[arg-type]
