import os
import time
from difflib import SequenceMatcher
from typing import Dict, Iterable, List, Optional

DATADOG_EVENTS_API = "https://api.datadoghq.com/api/v2/events"  # latest events API endpoint


def fetch_events(start, end, api_key=None, app_key=None, query=None, limit=100):
    """Fetch events from Datadog between start and end UNIX timestamps."""
    api_key = api_key or os.environ.get("DD_API_KEY")
    app_key = app_key or os.environ.get("DD_APP_KEY")
    if not api_key or not app_key:
        raise ValueError("API and application keys must be provided via args or env vars")
    params = {
        "filter[from]": int(start),
        "filter[to]": int(end),
        "page[limit]": limit,
    }
    if query:
        params["filter[query]"] = query

    headers = {
        "DD-API-KEY": api_key,
        "DD-APPLICATION-KEY": app_key,
    }
    
    import requests
    resp = requests.get(DATADOG_EVENTS_API, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    events = []
    for item in data.get("data", []):
        attrs = item.get("attributes", {}).copy()
        attrs["id"] = item.get("id")
        events.append(attrs)
    return events


def _string_similarity(a: Optional[str], b: Optional[str]) -> float:
    """Return a similarity ratio between two strings using SequenceMatcher."""
    return SequenceMatcher(None, a or "", b or "").ratio()


def _tag_similarity(a: Iterable[str], b: Iterable[str]) -> float:
    """Return Jaccard similarity between two tag iterables."""
    set_a, set_b = set(a or []), set(b or [])
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def _event_similarity(a: Dict, b: Dict, weights: Optional[Dict[str, float]] = None) -> float:
    """Combine title, text and tag similarity using weighted average."""
    weights = weights or {"title": 0.4, "text": 0.3, "tags": 0.3}
    title_sim = _string_similarity(a.get("title"), b.get("title"))
    text_sim = _string_similarity(a.get("text"), b.get("text"))
    tags_sim = _tag_similarity(a.get("tags", []), b.get("tags", []))
    return (
        weights.get("title", 0) * title_sim
        + weights.get("text", 0) * text_sim
        + weights.get("tags", 0) * tags_sim
    )


def group_events(
    events: Iterable[Dict],
    similarity_threshold: float = 0.6,
    weights: Optional[Dict[str, float]] = None,
) -> List[List[Dict]]:
    """Group events using a combined similarity of title, text and tags."""
    groups: List[List[Dict]] = []
    for ev in events:
        placed = False
        for group in groups:
            rep_ev = group[0]
            if _event_similarity(ev, rep_ev, weights) >= similarity_threshold:
                group.append(ev)
                placed = True
                break
        if not placed:
            groups.append([ev])
    return groups


def main():
    now = int(time.time())
    start = now - 3600  # past hour
    end = now
    events = fetch_events(start, end)
    groups = group_events(events)
    for idx, group in enumerate(groups, 1):
        print(f"\nGroup {idx} ({len(group)} events):")
        for ev in group:
            print(f" - {ev.get('title')}")


if __name__ == "__main__":
    main()
