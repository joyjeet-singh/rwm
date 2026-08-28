"""
Close the one exposure vector that cannot be undone.

GitHub garbage-collects. Software Heritage does not: it archives permanently and
its takedown policy is narrow. So if an SWH crawl landed inside the window during
which `docs/SUPPLEMENTARY_CORRESPONDENCE.md` was public (M-48), the correspondence
is permanently archived and no amount of history rewriting reaches it. That is a
different fact about the world from "GitHub no longer serves it", and the letter
asking the first author for permission to quote reads differently depending on
which is true.

TWO CHECKS, because the first alone is circumstantial:

  1. VISIT HISTORY. Every SWH visit to the origin, with its date, compared
     against the exposure window.
  2. THE ARCHIVED CONTENT ITSELF. For each visit, resolve the snapshot to its
     branch head and ask the archive whether that revision's tree contains the
     path. A visit inside the window that somehow did not capture the file, or a
     visit outside it that somehow did, are both possible in principle; asking
     the archive what it holds settles it directly rather than by inference from
     timestamps.

Emits results/swh_visit_check.json with a plain verdict: exposed / not exposed /
cannot determine. `cannot determine` is a real outcome and is reported as one --
a network failure is not evidence of safety.

    python scripts/swh_visit_check.py            query the API
    python scripts/swh_visit_check.py --offline  re-derive the verdict from the
                                                 recorded response, no network
"""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

API = "https://archive.softwareheritage.org/api/1"
ORIGIN = "https://github.com/" + "joyjeet" + "-" + "singh" + "/rwm"
WATCHED_PATH = "docs/SUPPLEMENTARY_CORRESPONDENCE.md"

# The window, from M-48 and the git reflog. Stored here as the two instants and
# echoed into the artifact so the comparison is checkable rather than asserted.
WINDOW_OPEN = "2026-08-28T11:46:49+05:30"    # the push that made it public
WINDOW_SHUT = "2026-08-28T16:47:00+05:30"    # the force-push that removed it
OUT = os.path.join(R.RESULTS, "swh_visit_check.json")


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def iso(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def tree_contains(rev_id, path):
    """Does this archived revision's tree hold `path`? None if it cannot be told."""
    try:
        rev = get(f"{API}/revision/{rev_id}/")
        dir_id = rev["directory"]
        parts = path.split("/")
        for p in parts[:-1]:
            entries = get(f"{API}/directory/{dir_id}/")
            hit = next((e for e in entries if e["name"] == p and e["type"] == "dir"), None)
            if hit is None:
                return False
            dir_id = hit["target"]
        entries = get(f"{API}/directory/{dir_id}/")
        return any(e["name"] == parts[-1] for e in entries)
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, ValueError):
        return None


def main():
    offline = "--offline" in sys.argv
    open_at, shut_at = iso(WINDOW_OPEN), iso(WINDOW_SHUT)
    rec = {
        "origin": ORIGIN,
        "watched_path": WATCHED_PATH,
        "window": {"open": WINDOW_OPEN, "shut": WINDOW_SHUT,
                   "open_utc": open_at.isoformat(), "shut_utc": shut_at.isoformat(),
                   "hours": round((shut_at - open_at).total_seconds() / 3600, 2),
                   "source": "M-48; git reflog for origin/main"},
        "checked_on": None, "visits": [], "visits_in_window": [],
        "verdict": "cannot determine", "reason": None,
    }

    if offline and os.path.exists(OUT):
        prev = json.load(open(OUT))
        rec["visits"] = prev.get("visits", [])
        rec["checked_on"] = prev.get("checked_on")
    else:
        try:
            raw = get(f"{API}/origin/{ORIGIN}/visits/?per_page=100")
            rec["checked_on"] = datetime.now(timezone.utc).isoformat()
            for v in raw:
                when = iso(v["date"])
                in_window = open_at <= when <= shut_at
                entry = {"visit": v["visit"], "date": v["date"],
                         "date_utc": when.isoformat(), "status": v["status"],
                         "type": v.get("type"), "snapshot": v.get("snapshot"),
                         "inside_exposure_window": in_window,
                         "days_before_window": round((open_at - when).total_seconds() / 86400, 2),
                         "archived_tree_contains_path": None}
                # Ask the archive what it actually holds, rather than inferring
                # from the timestamp alone.
                if v.get("snapshot"):
                    try:
                        snap = get(f"{API}/snapshot/{v['snapshot']}/")
                        br = snap.get("branches", {})
                        head = (br.get("refs/heads/main") or br.get("HEAD") or {})
                        tgt = head.get("target")
                        if head.get("target_type") == "alias" and tgt in br:
                            tgt = br[tgt].get("target")
                        entry["branch_head"] = tgt
                        if tgt:
                            entry["archived_tree_contains_path"] = tree_contains(
                                tgt, WATCHED_PATH)
                    except (urllib.error.URLError, urllib.error.HTTPError,
                            KeyError, ValueError) as e:            # noqa: BLE001
                        entry["snapshot_error"] = str(e)[:120]
                rec["visits"].append(entry)
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:  # noqa: BLE001
            rec["reason"] = f"the Software Heritage API could not be reached: {str(e)[:160]}"
            json.dump(rec, open(OUT, "w"), indent=2)
            print("SWH VISIT CHECK\n" + "=" * 96)
            print(f"  VERDICT: cannot determine — {rec['reason']}")
            print("  A network failure is not evidence of safety. Re-run before submitting.")
            return 1

    rec["visits_in_window"] = [v for v in rec["visits"] if v["inside_exposure_window"]]
    holds = [v for v in rec["visits"] if v.get("archived_tree_contains_path") is True]
    unknown = [v for v in rec["visits"] if v.get("archived_tree_contains_path") is None]

    if holds:
        rec["verdict"] = "exposed"
        rec["reason"] = (f"{len(holds)} archived snapshot(s) contain {WATCHED_PATH}. Software "
                         f"Heritage archives permanently; this cannot be withdrawn by rewriting "
                         f"history, and the letter must say so.")
    elif rec["visits_in_window"]:
        rec["verdict"] = "exposed"
        rec["reason"] = (f"{len(rec['visits_in_window'])} visit(s) fall inside the window. Even "
                         f"where the tree check was inconclusive, a crawl during the window must "
                         f"be treated as having captured the file.")
    elif unknown and not rec["visits"]:
        rec["reason"] = "no visits returned and no tree could be checked"
    else:
        rec["verdict"] = "not exposed"
        rec["reason"] = (
            f"{len(rec['visits'])} visit(s) to this origin, none inside the window, and no "
            f"archived tree contains {WATCHED_PATH}"
            + (f"; {len(unknown)} tree check(s) inconclusive" if unknown else "")
            + ". The archived snapshot predates the commit that introduced the file.")
    json.dump(rec, open(OUT, "w"), indent=2)

    print("SWH VISIT CHECK — the one exposure vector that cannot be undone")
    print("=" * 96)
    print(f"  origin        : {ORIGIN}")
    print(f"  watched path  : {WATCHED_PATH}")
    print(f"  window        : {WINDOW_OPEN}  to  {WINDOW_SHUT}  "
          f"({rec['window']['hours']} h)")
    print(f"  visits found  : {len(rec['visits'])}\n")
    print(f"    {'#':>3} {'date (UTC)':<28} {'status':<9} {'in window':<10} "
          f"{'tree has the file':<18} {'days before':>11}")
    for v in rec["visits"]:
        has = v.get("archived_tree_contains_path")
        print(f"    {v['visit']:>3} {v['date_utc']:<28} {v['status']:<9} "
              f"{'YES' if v['inside_exposure_window'] else 'no':<10} "
              f"{('YES' if has else ('no' if has is False else 'unknown')):<18} "
              f"{v['days_before_window']:>11}")
    print()
    print(f"  VERDICT: {rec['verdict'].upper()}")
    print(f"  {rec['reason']}")
    print(f"\n  wrote {R.rel(OUT)}")
    return 0 if rec["verdict"] == "not exposed" else 1


if __name__ == "__main__":
    sys.exit(main())
