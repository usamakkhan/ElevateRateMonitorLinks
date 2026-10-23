"""Refresh the Pages domain manifest after a dispatch or periodic server check."""
import datetime
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

MANIFEST = Path(__file__).resolve().parents[1] / "docs" / "domain.json"


def normalize(value):
    raw = str(value or "").strip()
    if not raw:
        raise ValueError("Empty domain")
    parsed = urlsplit(raw if "://" in raw else "https://" + raw)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Domain must be HTTPS without credentials")
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("Domain must not include a path, query, or fragment")
    return "https://" + parsed.netloc.lower()


def get_json(url):
    req = Request(url, headers={"User-Agent": "Elevate-domain-manifest/1"})
    with urlopen(req, timeout=10) as response:
        if response.status != 200:
            raise ValueError("Unexpected response")
        return json.load(response)


def main():
    current = json.loads(MANIFEST.read_text(encoding="utf-8"))
    primary = normalize(current["primary"])
    candidate = os.environ.get("NEW_DOMAIN", "").strip()
    if not candidate:
        reported = get_json(primary + "/api/site-domain")
        if not reported.get("success"):
            raise ValueError("Current server did not report a domain")
        candidate = reported.get("domain", "")
    candidate = normalize(candidate)
    if candidate == primary:
        print("Domain unchanged")
        return
    try:
        latest = get_json(candidate + "/api/latest")
        if not latest.get("success"):
            raise ValueError("New domain is not serving Elevate data")
    except Exception as exc:
        if os.environ.get("NEW_DOMAIN", "").strip():
            raise ValueError("New domain is not serving Elevate data") from exc
        print("Reported domain is not ready; keeping", primary)
        return
    previous = [primary] + [normalize(item) for item in current.get("fallbacks", [])]
    next_manifest = {
        "schema_version": 1,
        "primary": candidate,
        "fallbacks": list(dict.fromkeys(item for item in previous if item != candidate))[:3],
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    MANIFEST.write_text(json.dumps(next_manifest, indent=2) + "\n", encoding="utf-8")
    print("Updated domain to", candidate)


if __name__ == "__main__":
    main()
