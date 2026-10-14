import argparse
import json
from pathlib import Path
import sys
import tempfile

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(PROJECT / "src"))

from scripts.build_synthetic_history import build_history, synthetic_pair
from secret_history.reporting.report import as_csv, as_json
from secret_history.reporting.sarif import as_sarif
from secret_history.scanner import scan_repository


def verify(repository, expected=None):
    first = scan_repository(repository, detectors="all")
    second = scan_repository(repository, detectors="all")
    if first != second or first["summary"]["decisions"] != {"SUSPECTED_SECRET": 1}:
        raise ValueError("Unexpected demo result or unstable report")
    row = first["candidates"][0]
    if (row["path"], row["line_start"], row["line_end"]) != (".env", 2, 3) or not row["absent_from_reference_env"]:
        raise ValueError("Unexpected location")
    if expected and row["fingerprint"] != expected:
        raise ValueError("Stored fingerprint changed")
    output = as_json(first) + as_csv(first) + as_json(as_sarif(first))
    if any(value in output for value in synthetic_pair()):
        raise ValueError("Unmasked synthetic value in output")
    print(as_json({"verification": "OK", "commits": first["coverage"]["commits_scanned"], "alerts": 1,
                   "fingerprint": row["fingerprint"], "stable": True, "masked": True}), end="")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify synthetic history, stable fingerprint and masked exports.")
    parser.add_argument("--create", action="store_true", help="Build and remove a temporary synthetic history")
    args = parser.parse_args(argv)
    if args.create:
        temp_root = (PROJECT / "tmp").resolve()
        temp_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="demo-check-", dir=temp_root) as directory:
            destination = Path(directory).resolve() / "repo"
            if not destination.is_relative_to(temp_root):
                raise ValueError("Temporary path escaped workspace")
            build_history(destination)
            verify(destination)
    else:
        manifest = json.loads((PROJECT / "data/manifests/aws_pair_demo.json").read_text(encoding="utf-8-sig"))
        verify(PROJECT / "tests/synthetic_histories/generated/aws_pair_demo", manifest["expected"]["fingerprint"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print("Demo verification failed.", file=sys.stderr)
        raise SystemExit(2)
