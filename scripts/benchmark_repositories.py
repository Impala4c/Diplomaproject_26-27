import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from secret_history.git_history.reader import GitReader
from secret_history.reporting.report import as_json
from secret_history.scanner import scan_repository


def main(argv=None):
    parser = argparse.ArgumentParser(description="Benchmark previously downloaded public repositories locally.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--large-history-commits", type=int, default=1000)
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args(argv)
    if args.repeat < 1 or args.large_history_commits < 1:
        parser.error("Limits must be positive")
    args.output.mkdir(parents=True, exist_ok=False)
    summary = {"measured_at_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
               "platform": platform.platform(), "clock": "perf_counter; elapsed wall time; operating-system caches not cleared",
               "network_validation": False, "runs": []}
    for label in ("python-dotenv", "aws-cli", "github-cli"):
        repository = PROJECT / "data" / "repositories" / (label + ".git")
        reader = GitReader(repository)
        reference = reader.resolve("HEAD")
        local_refs = len(reader.run("for-each-ref", "--format=%(objectname)").splitlines())
        for repetition in range(1, args.repeat + 1):
            print(f"Scanning {label}, run {repetition}...", flush=True)
            start = time.perf_counter()
            report = scan_repository(repository, ref=reference, detectors="all",
                                     max_commits=None if label == "python-dotenv" else args.large_history_commits)
            duration = time.perf_counter() - start
            output_name = f"{label}.run{repetition}.json"
            with (args.output / output_name).open("x", encoding="utf-8") as handle:
                handle.write(as_json(report))
            coverage = report["coverage"]
            unique = {(row["blob_oid"], row["path"], row["line_start"], row["kind"]): row for row in report["candidates"]}
            result = {"repository": label, "reference_oid": reference, "local_refs": local_refs, "repetition": repetition,
                      "elapsed_seconds": round(duration, 3), "commits_per_second": round(coverage["commits_scanned"] / duration, 3),
                      "coverage": {key: value for key, value in coverage.items() if key not in ("skipped", "parse_warnings")},
                      "skipped_unique_locations_by_reason": dict(Counter(row["reason"] for row in coverage["skipped"])),
                      "parse_warning_locations": len(coverage["parse_warnings"]), "summary": report["summary"],
                      "unique_candidate_blob_locations": len(unique), "unique_alert_blob_locations": sum(row["status"] != "NON_SECRET" for row in unique.values()),
                      "report_file": output_name}
            summary["runs"].append(result)
            (args.output / "summary.json").write_text(as_json(summary), encoding="utf-8")
            print(json.dumps({"repository": label, "seconds": result["elapsed_seconds"], "commits": coverage["commits_scanned"], "alerts": report["summary"]["alerts"], "unique_alert_locations": result["unique_alert_blob_locations"]}), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print("Benchmark failed; partial results may be present. Check paths and repository objects.", file=sys.stderr)
        raise SystemExit(2)
